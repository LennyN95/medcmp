from typing import Union
from enum import Enum
import math, sys

class ComparisonOutcome(Enum):
  MISSING = "missing"
  EXTRA = "extra"
  TYPE_MISMATCH = "type_mismatch"
  VALUE_MISMATCH = "value_mismatch"
  VALUE_SIMILAR = "value_similar"
  VALUE_CLOSE = "value_close"
  VALUE_EXACT = "value_exact"

class ComparisonItem: 
  path: str
  src_value: any = None
  ref_value: any = None
  outcome: ComparisonOutcome = None
  precision: tuple = None


def get_data(file_path: str):
  """
  Read a json / yml file and return the data.
  """

  # check file type
  if file_path.endswith(".json"):
    import json
    with open(file_path, "r") as f:
      data = json.load(f)
  elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
    raise Exception("YAML not supported yet.")
    # import yaml
    # with open(file_path, "r") as f:
    #   data = yaml.load(f, Loader=yaml.FullLoader)
  else:
    raise Exception(f"Unknown file type: {file_path}")
  
  # return data
  return data

def scan_data_paths(d: Union[dict, list], base: str = ""):
  """
  recursively scan a data object and return a list of value paths
  """

  # collect a list of key items
  items = []

  # recursively iterate keys
  if isinstance(d, dict):
    for k, v in d.items():

      # absolute path to this key
      p = base + '.' + k if base else k

      # if dict or list, recursively iterate
      if isinstance(v, dict) or isinstance(v, list):
        items += scan_data_paths(v, p)
      else:
        items.append(p)

  elif isinstance(d, list):
    for i, v in enumerate(d):

      # absolute path to this key
      p = base + '.' + str(i) if base else str(i)

      # if dict or list, recursively iterate
      if isinstance(v, dict) or isinstance(v, list):
        items += scan_data_paths(v, p)
      else:
        items.append(p)

  # return results
  return items

def get_value(d, path):
  """
  Get a value from a dictionary using a path.
  """
  keys = path.split(".")
  
  for k in keys: 
    d = d[int(k)] if k.isnumeric() else d[k]
  
  return d

def precision_and_scale(x):
    # https://stackoverflow.com/questions/3018758/determine-precision-and-scale-of-particular-number-in-python
    max_digits = sys.float_info.dig
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(math.log10(int_part)) + 1
    if magnitude >= max_digits:
        return (magnitude, 0)
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    scale = int(math.log10(frac_digits))
    return (magnitude + scale, scale)

def compare_numbers(v1: Union[int, float], v2: Union[int, float], verbose: bool = False):

  # v1 and v2 must be of equal type and numeric
  assert type(v1) == type(v2)
  assert not isinstance(v1, bool)
  assert isinstance(v1, float) or isinstance(v1, int)

  # perfect matching
  if v1 == v2:
    return True, 1, math.inf
  
  # abort for scale missmatch
  if int(math.log10(v1)) != int(math.log10(v2)):
    return False, -1, -1

  # scale matching (for int and float)
  matching_scale = -1
  if math.log10(v1) >= 0:
    for i in range(int(math.log10(v1)) + 1):
      if round(v1 / 10**i) == round(v2 / 10**i):
        if verbose: print("B] v1 (",v1,") and v2 (",v2,") sclae", int(math.log10(v1)) + 1, "match at scale", 10**i)
        matching_scale = 10**i
        break

  # precision matching (float only)
  matching_precision = -1
  if isinstance(v1, float):
    for precision in range(sys.float_info.dig):
      if round(v1, precision) == round(v2, precision):
        if verbose:  print("C] v1 (",v1,") and v2 (",v2,") match at precision", precision, "(", round(v1, precision), "-", round(v2, precision), ")")
        matching_precision = precision

  # report results
  return False, matching_scale, matching_precision


def check_item(item: ComparisonItem):

  v1 = item.src_value
  v2 = item.ref_value

  # check type
  if type(v1) != type(v2):
    item.outcome =  ComparisonOutcome.TYPE_MISMATCH

  # check boolean values
  if isinstance(v1, bool):
    if v1 != v2:
      item.outcome =  ComparisonOutcome.VALUE_MISMATCH
    else:
      item.outcome =  ComparisonOutcome.VALUE_EXACT
    
  # cehck string values
  if isinstance(v1, str):
    if v1 != v2:
      item.outcome = ComparisonOutcome.VALUE_MISMATCH
    else:
      item.outcome = ComparisonOutcome.VALUE_EXACT

  # if numeric, check various precisions
  if (isinstance(v1, int) or isinstance(v1, float)) and not isinstance(v1, bool):
    match, scale, precision = compare_numbers(v1, v2)
    print("compare numbers", v1, "with", v2, " -> ", match, scale, precision)

    if match:
      item.outcome = ComparisonOutcome.VALUE_EXACT
    elif scale > 0:
      item.outcome = ComparisonOutcome.VALUE_SIMILAR
      item.precision = (scale, precision)
    else:
      item.outcome = ComparisonOutcome.VALUE_MISMATCH

  # check exact
  return ComparisonOutcome.VALUE_EXACT

def compare_data(src_file: str, ref_file: str):
  """
  Compare two json / yml files.
  - travel through all keys
  - identify missing key paths
  - identify extra key paths
  - compare values
  - for not exactly matching values try various precisions and report the best match
  """

  # read files
  src_data = get_data(src_file)
  ref_data = get_data(ref_file)

  # compare data
  src_paths = scan_data_paths(src_data)
  ref_paths = scan_data_paths(ref_data)

  # convert to compare items
  items = []

  for p in src_paths:
    item = ComparisonItem()
    items.append(item)
    item.path = p
    
    # check if path is in ref or if path is an extra path
    if not p in ref_paths:
      item.outcome = ComparisonOutcome.EXTRA
      continue

    # remove ref paths that are already matched
    ref_paths.remove(p)

    # get values
    item.src_value = get_value(src_data, p)
    item.ref_value = get_value(ref_data, p)

    # compare values
    check_item(item)

  # all remaining ref paths are missing
  for p in ref_paths:
    item = ComparisonItem()
    item.path = p
    item.outcome = ComparisonOutcome.MISSING
    items.append(item)

  # print d1 scan results
  print("\n\nscan results:")
  for item in items:
    print(item.path, item.outcome, item.src_value, item.ref_value, item.precision)


# test
if __name__ == "__main__":

  # compare two files
  compare_data("test/src/deep/more.json", "test/ref/deep/more.json")