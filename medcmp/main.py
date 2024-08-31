import sys
import os

from typing import Optional

from medcmp.Report import Report, ReportConsolePrint, ReportYamlExport
from medcmp.scan import compare_tree_structures
from medcmp.checks.FileCompare import FileCompare
from medcmp.checks.DataFileCheck import DataFileCheck
from medcmp.checks.ImageFileCheck import ImageFileCheck
from medcmp.checks.SizeCheck import SizeCheck
from medcmp.checks.DicomsegContentCheck import DicomsegContentCheck

def compare(src: str, ref: str, report: Optional[Report] = None, verbose: bool = False):
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


def main():
  
  # use arg1, arg2 and arg3 for src, ref and report path
  if len(sys.argv) >= 4:
    src_path = sys.argv[1]
    ref_path = sys.argv[2]
    report_path = sys.argv[3]
    report_name = sys.argv[4] if len(sys.argv) > 4 else None
  else:
    src_path = "/app/test/src"
    ref_path = "/app/test/ref"
    report_path = "/app/output/report.yml"
    report_name = None

  # print paths
  print("RUNNING MEDCMP ON")
  print("src_path:", src_path)
  print("ref_path:", ref_path)
  print("report_path:", report_path)
  print("report_name:", report_name)

  # create report
  report = Report(report_name)
  
  # print 
  print("report_id:", report.id)
  print("------------------")

  # compare
  compare(src_path, ref_path, report=report)

  # print report
  ReportConsolePrint(report).print()

  # export report
  ReportYamlExport(report).export(report_path)


if __name__ == "__main__":
  main()
