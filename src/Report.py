import os, yaml
from typing import Union

class Report:
  files_missing = []        # files missing in src
  files_extra = []          # files missing in ref
  checks = []               # list of checks

  def __init__(self):
    self.files_missing = []
    self.files_extra = []
    self.checks = []  

  def add(self, entry: 'ReportCheck'):
    self.checks.append(entry)

  def summarize(self) -> dict:
    
    cehcks_data = []
    checker_data = {}

    for check in self.checks:
      if check.checker not in checker_data: 
        checker_data[check.checker] = {
          #"files": [],
          "files": 0,
          "findings": {}
        }
      #checker_data[check.checker]["files"].append(check.path)
      checker_data[check.checker]["files"] += 1
      for finding in check.findings:
        if finding.label not in checker_data[check.checker]["findings"]:
          checker_data[check.checker]["findings"][finding.label] = 0
        checker_data[check.checker]["findings"][finding.label] += 1

    # reduce checker array to unique files

    data = {
      "files_missing": len(self.files_missing),
      "files_extra": len(self.files_extra),
      "checks": checker_data
    }

    return data

  def conclude(self) -> bool:
    return len(self.files_missing) == 0 and len(self.files_extra) == 0 and all([len(check.findings) == 0 for check in self.checks])

class ReportCheck:

  def __init__(self, path: str, checker: str, meta: dict = {}):
    self.path = path
    self.checker = checker
    self.findings = []
    self.notes = []
    self.meta = meta

  def add(self, fact: Union['ReportCheckFinding', 'ReportCheckNote']):
    if isinstance(fact, ReportCheckNote):
      self.notes.append(fact)
    elif isinstance(fact, ReportCheckFinding):
      self.findings.append(fact)
    else:
      raise ValueError("Invalid fact type (must be either finding or note).")

class ReportCheckFinding:
  subpath: str
  label: str
  description: str
  info: any

  def __init__(self, label: str, description: str, info: any, subpath: str = ""):
    self.subpath = subpath
    self.label = label
    self.description = description
    self.info = info

class ReportCheckNote:
  subpath: str
  label: str
  description: str
  info: any

  def __init__(self, label: str, description: str, info: any, subpath: str = ""):
    self.subpath = subpath
    self.label = label
    self.description = description
    self.info = info

class ReportConsolePrint:

  def __init__(self, report: Report):
    self.report = report

  def print(self):

    # print missing files
    if len(self.report.files_missing) > 0:
      print("Files missing from reference:")
      for missing_path in self.report.files_missing:
        print(f"  {missing_path}")

    # print extra files
    if len(self.report.files_extra) > 0:
      print("Extra files not in reference:")
      for extra_path in self.report.files_extra:
        print(f"  {extra_path}")

    # print all cheks notes and findings
    if len(self.report.checks) > 0:
      print("All checks:")
      for check in self.report.checks:
        print(f"  {check.path}")
        print(f"    checker: {check.checker}")
        # print(f"    meta: {finding.meta}")
        for finding in check.findings:
          print(f"F    {finding.subpath}: {finding.label} ({finding.info})")
        for note in check.notes:
          print(f"N    {note.subpath}: {note.label} ({note.info})")

class ReportYamlExport:

  def __init__(self, report: Report):
    self.report = report

  def generate(self):
    data = {}

    # add missing files
    if len(self.report.files_missing) > 0:
      data["missing_files"] = self.report.files_missing

    # add extra files
    if len(self.report.files_extra) > 0:
      data["extra_files"] = self.report.files_extra

    # grouping by paths
    file_checks = {}
    if len(self.report.checks):
      for check in self.report.checks:
        if check.path not in file_checks:
          file_checks[check.path] = []
        file_checks[check.path].append(check)

    # add all findings
    if len(self.report.checks) > 0:
      data["checked_files"] = []
      
      for path, checks in file_checks.items():
        checked_file = {
          "file": os.path.basename(path),
          "path": path,
          "checks": []
        }
        
        for check in checks:
          item = {}
          item["checker"] = check.checker
          #item["meta"] = finding.meta
                
          # add notes
          item["notes"] = []
          for note in check.notes:
            note_item = {}
            note_item["label"] = note.label
            note_item["description"] = note.description
            if note.subpath: 
              note_item["subpath"] = note.subpath
            if note.info:
              note_item["info"] = note.info
            item["notes"].append(note_item)
            
          # add findings
          item["findings"] = []
          for finding in check.findings:
            fact_item = {}
            fact_item["label"] = finding.label
            fact_item["description"] = finding.description
            if finding.subpath: 
              fact_item["subpath"] = finding.subpath
            if finding.info:
              fact_item["info"] = finding.info
            item["findings"].append(fact_item)

          # remove empty findings and empty notes from item
          if len(item["notes"]) == 0:
            del item["notes"]
            
          if len(item["findings"]) == 0:
            del item["findings"]

          # add item to file cheks
          checked_file["checks"].append(item)
          
        # add file checks to data
        data["checked_files"].append(checked_file)

    # add summary (remove all empty finding objects to reduce size)
    # NOTE: report summary only contains findings (not notes)
    report_summary = self.report.summarize()
    for checker in report_summary["checks"]:
      if not bool(report_summary["checks"][checker]["findings"]):
        del report_summary["checks"][checker]["findings"]
    data["summary"] = report_summary

    # add conclusion
    data["conclusion"] = self.report.conclude()

    # return generated data
    return data
  
  def export(self, path: str):
  
    # generate
    data = self.generate()

    # write yaml file
    with open(path, "w") as f:
      yaml.dump(data, f, sort_keys=False, indent=2)