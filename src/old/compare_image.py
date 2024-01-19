import pyplastimatch as pypla
import numpy as np

def compare_images(src_path: str, ref_path: str, tolerance: int = 0, verbose: bool = False):
  """ 
  Compare two images.
  """

  # read images
  dice_summary_dict = pypla.dice(
      path_to_reference_img=ref_path,
      path_to_test_img=src_path,
  )

  # get dice score
  dice_score = dice_summary_dict["dc"]

  # return result
  print("dice_summary_dict: ",  dice_score)

  # return conclusion
  return np.isclose(dice_score, 1.0, atol=tolerance)

# test
if __name__ == "__main__":

  # compare two files
  #compare_data("test/src/deep/more.json", "test/ref/deep/more.json")
  compare_images("test/src/deep/100058.cacpred.seg.nii.gz", "test/ref/deep/100058.cacpred.seg.nii.gz")