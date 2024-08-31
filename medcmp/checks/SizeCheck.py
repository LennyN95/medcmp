from .FileCompare import FileCheck
import os

class SizeCheck(FileCheck):

  def can_check(self) -> bool:
    return not self.src_path.endswith(".dcm") \
      and  not self.src_path.endswith(".nii.gz") \
      and  not self.src_path.endswith(".nrrd") \
      and  not self.src_path.endswith(".mha")

  def check(self) -> bool:

    # load file size
    src_size = os.path.getsize(self.src_path)
    ref_size = os.path.getsize(self.ref_path)
    diff_size = src_size - ref_size

    # compile finding info data
    info = {
      'src_size': src_size,
      'ref_size': ref_size,
      'diff_size': diff_size
    }

    # report facts
    if src_size > ref_size:
      self.add_finding("Size Difference", "file size is larger than reference", info)
    elif src_size < ref_size:
      self.add_finding("Size Difference", "file size is smaller than reference", info)

    # return check passed / failed
    return src_size == ref_size

