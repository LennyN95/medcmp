
import os, hashlib
from enum import Enum

class FileType(Enum):
  RAW = "raw"
  DATA = "data"
  LABELMAP = "labelmap"

class Item:
  base: str = None
  path: str = None
  name: str = None
  size: int = None
  type: FileType = None

  @property
  def relpath(self) -> str:
    return os.path.relpath(self.path, self.base)

  @property
  def hash(self) -> str:
    hstr = f"{len(self.relpath)}||{self.relpath}||{self.size}"
    return hashlib.md5(hstr.encode()).hexdigest()


def scan_tree(base: str):
  """
  Scan a directory into a list of files and extract file metadata.
  """

  # collect a list of file items
  items = {}

  # recursively iterate folder under path
  for root, _, files in os.walk(base):
    for name in files:

      # get full path
      path = os.path.join(root, name)

      # get file size
      size = os.path.getsize(path)

      # create a new item
      item = Item()
      item.base = base
      item.path = path
      item.name = name
      item.size = size

      # add to list
      items[item.relpath] = item

  # return results
  return items


# test
if __name__ == "__main__":

  src_path = "test/src"
  ref_path = "test/ref"

  # scan trees
  src_items = scan_tree(src_path)
  ref_items = scan_tree(ref_path)

  # collect files that are in src and ref and will be compared on a content level
  cmp_items = {}
  extra_items = {}
  missing_items = {}

  # find all items in src that are not in ref (extra files)
  for hash, src_item in src_items.items():
    if hash not in ref_items:
      extra_items[hash] = src_item
    else:
      ref_item = ref_items[hash]
      cmp_items[hash] = (src_item, ref_item)

  # find all items in ref that are not in src (missing files)
  for hash, ref_item in ref_items.items():
    if hash not in src_items:
      missing_items[hash] = ref_item

  # print results
  print("\n\nextra items:", len(extra_items))
  for hash, src_item in extra_items.items():
    print(src_item.hash, src_item.base, src_item.path, src_item.name, src_item.size)

  print("\n\nmissing items:", len(missing_items))
  for hash, ref_item in missing_items.items():
    print(ref_item.hash, ref_item.base, ref_item.path, ref_item.name, ref_item.size)

  print("\n\ncompare items:", len(cmp_items))
  for hash, (src_item, ref_item) in cmp_items.items():
    print(src_item.hash, src_item.base, src_item.path, src_item.name, src_item.size)
    print(ref_item.hash, ref_item.base, ref_item.path, ref_item.name, ref_item.size)

    # compare file size
    if src_item.size != ref_item.size:
      print("size mismatch")
      continue

    # compare file hash
    if src_item.hash != ref_item.hash:
      print("hash mismatch")
      continue

    # compare file content
    with open(src_item.path, "rb") as src_file:
      with open(ref_item.path, "rb") as ref_file:
        src_content = src_file.read()
        ref_content = ref_file.read()

        if src_content != ref_content:
          print("content mismatch")
          continue


    print("")
