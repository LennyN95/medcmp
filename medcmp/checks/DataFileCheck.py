from .FileCompare import FileCheck
from typing import Union, Optional, Any
from enum import Enum
import math
import sys
import yaml
import json
import csv

class ComparisonOutcome(Enum):
  UNDEFINED = "undefined"
  MISSING = "missing"
  EXTRA = "extra"
  TYPE_MISMATCH = "type_mismatch"
  VALUE_MISMATCH = "value_mismatch"
  VALUE_SIMILAR = "value_similar"
  VALUE_CLOSE = "value_close"
  VALUE_EXACT = "value_exact"

class ComparisonItem: 
  path: str
  type: Optional[str] = None
  src_value: Any = None
  ref_value: Any = None
  outcome: ComparisonOutcome = ComparisonOutcome.UNDEFINED
  info: Any = None
  #precision: tuple = None

def get_data(file_path: str):
  """
  Read a json / yml file and return the data.
  """

  # check file type
  if file_path.endswith(".json"):
    with open(file_path, "r") as f:
      data = json.load(f)
  elif file_path.endswith(".yml") or file_path.endswith(".yaml"):
    with open(file_path, "r") as f:
      data = yaml.load(f, Loader=yaml.FullLoader)
  elif file_path.endswith(".csv"):
    with open(file_path, "r") as f:
      reader = csv.DictReader(f)
      data = [row for row in reader]
      print("RECEIVED CSV DATA")
      print(data)
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
      p = base + '.' + f'[{i}]' if base else f'[{i}]'

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
    d = d[int(k[1:-1])] if k.startswith("[") else d[k]
  
  return d

def round_down(value, decimals):
  # factor = 1 / (10 ** decimals)
  # return (value // factor) * factor

  # factor = 10 ** decimals
  # return  math.ceil(value * factor) / factor
  
  value_str = str(value)
  decimal_index = value_str.find(".")
  return float(value_str[:decimal_index + decimals + 1])

def compare_numbers(v1: Union[int, float], v2: Union[int, float], verbose: bool = False):

  # v1 and v2 must be of equal type and numeric
  assert type(v1) == type(v2) # noqa: E721
  assert not isinstance(v1, bool)
  assert isinstance(v1, float) or isinstance(v1, int)

  # perfect matching
  if v1 == v2:
    return True, 1, math.inf
  
  # abort for scale missmatch
  if int(math.log10(v1)) != int(math.log10(v2)):
    return False, -1, -1

  # scale matching (for int and float)
  matching_scale = 1
  if math.log10(v1) >= 0:
    for i in range(int(math.log10(v1)) + 1):
      if int(v1 / 10**i) == int(v2 / 10**i):
        if verbose: 
          print("B] v1 (", int(v1 / 10**i) ,") and v2 (", int(v2 / 10**i) ,") scale", int(math.log10(v1)) + 1, "match at scale", 10**i)
        matching_scale = 10**i
        break

  # precision matching (float only)
  matching_precision = -1
  if isinstance(v1, float):
    for precision in range(sys.float_info.dig):
      if round_down(v1, precision) == round_down(v2, precision):
        if verbose:  
          print("C] v1 (",v1,") and v2 (",v2,") match at precision", precision, "(", round_down(v1, precision), "-", round_down(v2, precision), ")")
        matching_precision = precision

  # report results
  return False, matching_scale, matching_precision

def check_item(item: ComparisonItem):

  v1 = item.src_value
  v2 = item.ref_value

  # check type
  if type(v1) != type(v2): # noqa: E721
    item.outcome = ComparisonOutcome.TYPE_MISMATCH
    item.info = {
      'src': {'value': v1, 'type': type(v1).__name__},
      'ref': {'value': v2, 'type': type(v2).__name__}
    }
    return 
  
  # set type
  item.type = type(v1).__name__

  # check boolean values
  if isinstance(v1, bool):
    if v1 != v2:
      item.outcome = ComparisonOutcome.VALUE_MISMATCH
      item.info = {
        'src': v1,
        'ref': v2
      }
    else:
      item.outcome = ComparisonOutcome.VALUE_EXACT

    return
    
  # cehck string values
  if isinstance(v1, str):
    if v1 != v2:
      item.outcome = ComparisonOutcome.VALUE_MISMATCH
      item.info = {
        'src': v1,
        'ref': v2
      }
    else:
      item.outcome = ComparisonOutcome.VALUE_EXACT

    return

  # if numeric, check various precisions
  if (isinstance(v1, int) or isinstance(v1, float)) and not isinstance(v1, bool):
    match, scale, precision = compare_numbers(v1, v2, verbose=False)
    #print("compare numbers", v1, "with", v2, " -> ", match, scale, precision)

    if match:
      item.outcome = ComparisonOutcome.VALUE_EXACT
    elif scale > 0:
      item.outcome = ComparisonOutcome.VALUE_SIMILAR
      item.info = {
        'scale': scale, 
        'precision': precision,
        'src': v1,
        'ref': v2
      }
    else:
      item.outcome = ComparisonOutcome.VALUE_MISMATCH
      item.info = {
        'src': v1,
        'ref': v2
      }

class DataFileCheck(FileCheck):

  def can_check(self):
    return self.src_path.endswith(".json") \
        or self.src_path.endswith(".yml") \
        or self.src_path.endswith(".yaml") \
        or self.src_path.endswith(".csv")

  def check(self):
    """
    Compare two json / yml files.
    - travel through all keys
    - identify missing key paths
    - identify extra key paths
    - compare values
    - for not exactly matching values try various precisions and report the best match
    """

    # read files
    src_data = get_data(self.src_path)
    ref_data = get_data(self.ref_path)

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
      if p not in ref_paths:
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

    # wheather check passed or failes
    check_passed = True

    # overview (notes)
    exact_value_paths = [item.path for item in items if item.outcome == ComparisonOutcome.VALUE_EXACT]
    exact_value_paths_str = ",".join(exact_value_paths) if len(exact_value_paths) < 20 else ",".join(exact_value_paths[:20]) + " (+ " + str(len(exact_value_paths) - 20) + " more)"
    if len(exact_value_paths) > 0:
      self.add_note("Value Match", "These keys have identical values", exact_value_paths_str)
        
    # conclusion (findings)
    for item in items:

      # add facts to report for each item outcome
      if item.outcome == ComparisonOutcome.MISSING:
        self.add_finding("Missing key", f"Key '{item.path}' is missing in source file", item.info, subpath=item.path)
      elif item.outcome == ComparisonOutcome.EXTRA:
        self.add_finding("Extra key", f"Key '{item.path}' is extra in source file", item.info, subpath=item.path)
      elif item.outcome == ComparisonOutcome.TYPE_MISMATCH:
        self.add_finding("Type mismatch", f"Type of key '{item.path}' is different in source file", item.info, subpath=item.path)
      elif item.outcome == ComparisonOutcome.VALUE_MISMATCH:
        self.add_finding("Value mismatch", f"Value of key '{item.path}' is different in source file", item.info, subpath=item.path)
      elif item.outcome == ComparisonOutcome.VALUE_SIMILAR:
        self.add_finding("Value similar", f"Value of key '{item.path}' is similar in source file", item.info, subpath=item.path)

      if item.outcome != ComparisonOutcome.VALUE_EXACT:
        check_passed = False

    # return check passed result
    return check_passed













