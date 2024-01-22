from .FileCompare import FileCheck
import pyplastimatch as pypla 
import numpy as np

class ImageFileCheck(FileCheck):

  tolerance: float = 0.0001

  def can_check(self) -> bool:
    return self.src_path.endswith(".nii.gz") \
        or self.src_path.endswith(".nrrd") \
        or self.src_path.endswith(".mha")

  def check(self) -> bool:

    # read images
    dice_summary_dict = pypla.dice(
        path_to_reference_img=self.ref_path,
        path_to_test_img=self.src_path,
    )

    # get dice score
    dice_score = dice_summary_dict["dc"]

    # return conclusion
    self.fact("Dice Score", "Dice score between reference and test image", dice_score)

    # return report entry
    return np.isclose(dice_score, 1.0, atol=self.tolerance)