from abc import ABC, abstractmethod
from typing import List, Type, Optional
from Report import Report, ReportEntry, ReportEntryFact

class FileCompare:

  report: Report
  checks: List[Type['FileCheck']]

  def __init__(self, report: Report):
    self.report = report
    self.checks = []

  def register(self, check: 'FileCheck'):
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
    self.facts: List[ReportEntryFact] = []

  @abstractmethod
  def can_check(self) -> bool:
    pass

  @abstractmethod
  def check(self) -> bool:
      pass
  
  def fact(self, label: str, description: str, value: any, subpath: str = ""):
    self.facts.append(ReportEntryFact(label, description, value, subpath))

  def report(self) -> ReportEntry:
    entry = ReportEntry(self.src_path, self.__class__.__name__, {})
    entry.facts = self.facts
    return entry

  def run(self) -> Optional[ReportEntry]:
    if self.can_check():
      check_passed = self.check()
      return self.report()
    else:
      return None
    

