from abc import ABC, abstractmethod
from typing import List, Type, Optional, Any
from medcmp.Report import Report, ReportCheck, ReportCheckFinding, ReportCheckNote

class FileCompare:

  report: Report
  checks: List[Type['FileCheck']]

  def __init__(self, report: Report):
    self.report = report
    self.checks = []

  def register(self, check: type):
    assert issubclass(check, FileCheck)
    assert check not in self.checks
    self.checks.append(check)

  def compare(self, src_path: str, ref_path: str):

    # run all registered checks
    for check in self.checks:

      # run check and get results
      entry = check(src_path, ref_path).run()

      # add results to report
      if entry is not None:
        self.report.add(entry)
        

class FileCheck(ABC):

  def __init__(self, src_path: str, ref_path: str):
    self.src_path = src_path
    self.ref_path = ref_path
    self.findings: List[ReportCheckFinding] = []
    self.notes: List[ReportCheckNote] = []

  @abstractmethod
  def can_check(self) -> bool:
    pass

  @abstractmethod
  def check(self) -> bool:
      pass
  
  def add_finding(self, label: str, description: str, value: Any, subpath: str = ""):
    self.findings.append(ReportCheckFinding(label, description, value, subpath))

  def add_note(self, label: str, description: str, value: Any, subpath: str = ""):
    self.notes.append(ReportCheckNote(label, description, value, subpath))

  def report(self) -> ReportCheck:
    entry = ReportCheck(self.src_path, self.__class__.__name__, {})
    entry.findings = self.findings
    entry.notes = self.notes
    return entry

  def run(self) -> Optional[ReportCheck]:
    if self.can_check():
      try:
        _ = self.check()
      except Exception as e:
        self.add_finding("Exception", "An exception occurred during check", str(e))
      return self.report()
    else:
      return None
    

