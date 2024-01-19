from abc import ABC, abstractmethod
from typing import List, Type

class FileCompare:

  checks: List[Type['FileCheck']] = []

  def register(self, check: 'FileCheck'):
    assert issubclass(check, FileCheck)
    assert check not in self.checks
    self.checks.append(check)

  def compare(self, src_path: str, ref_path: str):
    for check in self.checks:
      check(src_path, ref_path).run()
        

class FileCheck(ABC):

  def __init__(self, src_path: str, ref_path: str):
    self.src_path = src_path
    self.ref_path = ref_path

  @abstractmethod
  def can_check(self):
    pass

  @abstractmethod
  def check(self):
      pass
  
  def run(self):
    if self.can_check():
      return self.check()
    else:
      return None
    

