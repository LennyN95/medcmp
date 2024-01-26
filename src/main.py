from Report import Report, ReportConsolePrint, ReportYamlExport
from scan import compare_tree_structures
from checks.FileCompare import FileCompare
from checks.DataFileCheck import DataFileCheck
from checks.ImageFileCheck import ImageFileCheck
from checks.SizeCheck import SizeCheck
from checks.DicomsegContentCheck import DicomsegContentCheck
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
  file_checker.register(DicomsegContentCheck)

  for relpath in comparable_files:
    src_path = os.path.join(src, relpath)
    ref_path = os.path.join(ref, relpath)

    file_checker.compare(src_path, ref_path)

  # return report
  return report


if __name__ == "__main__":

  # use arg1, arg2 and arg3 for src, ref and report path
  if len(sys.argv) == 4:
    src_path = sys.argv[1]
    ref_path = sys.argv[2]
    report_path = sys.argv[3]
  else:
    src_path = "/app/test/src"
    ref_path = "/app/test/ref"
    report_path = "/app/output/report.yml"

  # print paths
  print("RUNNING MEDCMP ON")
  print("src_path:", src_path)
  print("ref_path:", ref_path)
  print("report_path:", report_path)

  # compare
  report = compare(src_path, ref_path)

  # print report
  ReportConsolePrint(report).print()

  # export report
  ReportYamlExport(report).export(report_path)
