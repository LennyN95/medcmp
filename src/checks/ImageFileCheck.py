from .FileCompare import FileCheck
import pyplastimatch as pypla 
import numpy as np
import SimpleITK as sitk
import subprocess
from typing import Dict

class ImageFileCheck(FileCheck):

  dice_tolerance: float = 0.0001
  value_tolerance: float = 0.001

  def can_check(self) -> bool:
    return self.src_path.endswith(".nii.gz") \
        or self.src_path.endswith(".nrrd") \
        or self.src_path.endswith(".mha")

  def check(self) -> bool:
    
    # load ref image into numpy array
    ref_img = sitk.ReadImage(self.ref_path)
    ref_np = sitk.GetArrayFromImage(ref_img)
    
    # add note for file data type
    self.add_note("Data Type", "Data type of the reference image", str(ref_np.dtype))
    
    # if type is float run value checks only
    # e.g., probability maps, heatmaps, etc.
    if ref_np.dtype == np.float32 or ref_np.dtype == np.float64:
    
      # check values
      return self.check_values()
      
    else:

      # check dice
      return self.check_dice()
  
  
  def check_values(self) -> bool:
  
    # calculate the diff image between src and ref
    diff_img = pypla_compare(
        path_to_reference_img=self.ref_path,
        path_to_test_img=self.src_path,
    )

    # return conclusion
    self.add_note("Image Diff Stat", "Statistics of the diff image between src and ref.", diff_img)

    # check that MIN and MAX are within tolerance
    check = np.isclose(diff_img["MIN"], 0.0, atol=self.value_tolerance) \
        and np.isclose(diff_img["MAX"], 0.0, atol=self.value_tolerance)

    # add finding if check fails
    if not check:
      self.add_finding("Image Diff Stat", "Difference between reference and test image exceeds tolerance.", {"MIN": diff_img["MIN"], "MAX": diff_img["MAX"], "tolerance": self.value_tolerance})
      
    return check

  def check_dice(self) -> bool:
    
    # calculate dice between images
    dice_summary_dict = pypla.dice(
        path_to_reference_img=self.ref_path,
        path_to_test_img=self.src_path,
    )

    # get dice score
    dice_score = dice_summary_dict["dc"]

    # add note
    self.add_note("Dice Score", "Dice score between reference and test image", dice_score)

    # return report entry
    check = np.isclose(dice_score, 1.0, atol=self.dice_tolerance)
    
    # add finding if check fails
    if not check:
      self.add_finding("Dice Score Difference", "Dice score between reference and test image exceeds tolerance.", {"dice_score": dice_score, "tolerance": self.dice_tolerance})   
      
    return check
  
  
## helper until pyplastimatch.compare is available
def pypla_compare(path_to_reference_img, path_to_test_img, verbose = True) -> Dict[str, float]:
  """
  The compare command compares two files by subtracting one file from the other, and reporting statistics of the difference image. The two input files must have the same geometry (origin, dimensions, and voxel spacing). The command line usage is given as follows:
  
  For additional details, see:
  https://plastimatch.org/plastimatch.html#plastimatch-compare
  
  Args:
      path_to_reference_img:
      path_to_test_img:
      
  Returns:
      dictionary:
        MIN      Minimum value of difference image
        AVE      Average value of difference image
        MAX      Maximum value of difference image
        MAE      Mean average value of difference image
        MSE      Mean squared difference between images
        DIF      Number of pixels with different intensities
        NUM      Total number of voxels in the difference image
     
  """
  
  # print
  if verbose: 
    print("\n Comparing two images with 'plastimatch compare'")

  # build command
  bash_command = []
  bash_command += ["plastimatch", "compare"]
  bash_command += [path_to_reference_img, path_to_test_img]
  
  # run command
  dice_summary = subprocess.run(bash_command, capture_output = True, check = True)
  
  # print
  if verbose: 
    print("... Done.")

  # combine output
  comparison_raw = dice_summary.stdout.decode('utf-8')

  # flaten output
  comparison_flat = " ".join(comparison_raw.splitlines()).split()
  assert len(comparison_flat) == 14, "Unfamiliar output."
  
  # parse output into dictionary
  comparison_dict = {}
  for i in range(0, len(comparison_flat), 2):
    comparison_dict[comparison_flat[i]] = float(comparison_flat[i+1])
    
  # return dictionary
  return comparison_dict
