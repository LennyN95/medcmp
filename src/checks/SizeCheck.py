from .FileCompare import FileCheck
import os

class SizeCheck(FileCheck):

  def can_check(self) -> bool:
    return True

  def check(self) -> bool:

    # load file size
    src_size = os.path.getsize(self.src_path)
    ref_size = os.path.getsize(self.ref_path)

    # report facts
    if src_size > ref_size:
      self.fact("Size Difference", "file size is larger than reference", src_size - ref_size)
    elif src_size < ref_size:
      self.fact("Size Difference", "file size is smaller than reference", src_size - ref_size)

    # return check passed / failed
    return src_size == ref_size

