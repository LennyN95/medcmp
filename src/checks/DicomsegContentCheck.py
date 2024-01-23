from .FileCompare import FileCheck
import pydicom
import pydicom_seg
import SimpleITK as sitk

def compute_overlap(itksegimage1, itksegimage2):
    # Load segmentation volumes

    # Compute the overlap between the segmentations
    overlap_filter = sitk.LabelOverlapMeasuresImageFilter()
    overlap_filter.Execute(itksegimage1, itksegimage2)

    # Get the overlap measures
    dice_coefficient = overlap_filter.GetDiceCoefficient()

    return dice_coefficient

class DicomsegContentCheck(FileCheck):

  verbose: bool = True
  dc_thresh: float = 0.99

  def can_check(self) -> bool:
    return self.src_path.endswith(".seg.dcm") 

  def check(self) -> bool:

   if self.verbose:
    print("\nComparing DICOM SEG files...")

    print("Output file:", self.src_path)
    print("Reference file:", self.ref_path)

    dcm = pydicom.dcmread(self.src_path)
    reader = pydicom_seg.SegmentReader()
    output_seg = reader.read(dcm)

    dcm = pydicom.dcmread(self.ref_path)
    reader = pydicom_seg.SegmentReader()
    reference_seg = reader.read(dcm)

    if len(output_seg.available_segments) != len(reference_seg.available_segments):
      print(">>> The DICOM SEG files store a different number of segments")
      return False

    for segment_number in output_seg.available_segments:
      output_segment = output_seg.segment_image(segment_number)
      reference_segment = reference_seg.segment_image(segment_number)

      try:
        dc = compute_overlap(output_segment, reference_segment)

        # FIXME: how do we aggregate the DCs for each segment?
        if dc < self.dc_thresh:
          print(">>> DICOM SEG segments #%g are not equal (DC/DC threshold: %g/%g)"%(segment_number, dc, self.dc_thresh))
          self.fact("Dice Score Difference", "Dice score between reference and test image", dc, subpath="segment #%g"%segment_number)
          return False

      except Exception as e:
        print(">>> DICOM SEG segment #%g could not be compared"%segment_number)
        self.fact("Comparison Fail", str(e), -1, subpath="segment #%g"%segment_number)   

    print(">>> The DICOM SEG files are equal (DC threshold: %g)"%self.dc_thresh)
    return True