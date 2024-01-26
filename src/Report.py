import yaml

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
    self.meta = meta

  def add(self, fact: 'ReportCheckFinding'):
    self.findings.append(fact)

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

    # print all findings
    if len(self.report.checks) > 0:
      print("All checks:")
      for check in self.report.checks:
        print(f"  {check.path}")
        print(f"    checker: {check.checker}")
        # print(f"    meta: {finding.meta}")
        for finding in check.findings:
          print(f"    {finding.subpath}: {finding.label} ({finding.info})")

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

    # add all findings
    if len(self.report.checks) > 0:
      data["checked_files"] = []
      for check in self.report.checks:
        item = {}
        item["path"] = check.path
        item["checker"] = check.checker
        #item["meta"] = finding.meta
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

        # remove empty findings 
        if len(item["findings"]) == 0:
          del item["findings"]

        data["checked_files"].append(item)

    # add summary (remove all empty finding objects to reduce size)
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