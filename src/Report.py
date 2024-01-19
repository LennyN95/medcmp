from checks.DataFileCheck import ComparisonOutcome 

class Report:
  files_missing = []        # files missing in src
  files_extra = []          # files missing in ref
  files_check = []          # files that are in src and ref and will be checked
  files_sizediff = []       # files that are in src and ref but have different size
  content_same = []         # files that are in src and ref and have the same content
  content_diff = []         # files that are in src and ref and have different content
  content_similar = []      # files that are in src and ref and have similar content


class ReportConsolePrint:

  def __init__(self, report: Report):
    self.report = report

  def print(self):

    # print missing files
    if len(self.report.files_missing) > 0:
      print("Files missing from reference:")
      for item in self.report.files_missing:
        print(f"  {item.path}")

    # print extra files
    if len(self.report.files_extra) > 0:
      print("Extra files not in reference:")
      for item in self.report.files_extra:
        print(f"  {item.path}")

    # print different files
    if len(self.report.files_different) > 0:
      print("Files different from reference:")
      for item in self.report.files_different:
        print(f"  {item.path}")

    # print details about different files
    if len(self.report.files_different) > 0:
      print("Details about files different from reference:")
      for item in self.report.files_different:
        print(f"  {item.path}")
        print(f"    src: {item.src_value}")
        print(f"    ref: {item.ref_value}")
        print(f"    outcome: {item.outcome}")
        if item.outcome == ComparisonOutcome.VALUE_SIMILAR:
          print(f"    precision: {item.precision}")