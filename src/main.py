from Report import Report, ReportConsolePrint
from scan import compare_tree_structures
from checks.FileCompare import FileCompare
from checks.DataFileCheck import DataFileCheck
from checks.ImageFileCheck import ImageFileCheck
from checks.SizeCheck import SizeCheck
import sys, os


def compare(src: str, ref: str, report: Report = None, verbose: bool = False):
  """
  Compare two directories.
  """

  # create report if not provided
  if report is None:
    report = Report()

  # compare tree structures
  comparable_files = compare_tree_structures(src, ref, report)

  # compare files 
  file_checker = FileCompare(report)
  file_checker.register(DataFileCheck)
  file_checker.register(ImageFileCheck)
  file_checker.register(SizeCheck)

  for relpath in comparable_files:
    src_path = os.path.join(src, relpath)
    ref_path = os.path.join(ref, relpath)

    file_checker.compare(src_path, ref_path)

  # return report
  return report


if __name__ == "__main__":

  src_path = "/app/test/src"
  ref_path = "/app/test/ref"

  # compare
  report = compare(src_path, ref_path)

  # print report
  ReportConsolePrint(report).print()