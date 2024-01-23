import yaml

class Report:
  files_missing = []        # files missing in src
  files_extra = []          # files missing in ref
  files_check = []          # files that are in src and ref and will be checked
  files_sizediff = []       # files that are in src and ref but have different size
  content_same = []         # files that are in src and ref and have the same content
  content_diff = []         # files that are in src and ref and have different content
  content_similar = []      # files that are in src and ref and have similar content

  findings = []             # list of findings

  def add(self, entry: 'ReportEntry'):
    self.findings.append(entry)

class ReportEntry:

  def __init__(self, path: str, checker: str, meta: dict = {}):
    self.path = path
    self.checker = checker
    self.facts = []
    self.meta = meta

  def add(self, fact: 'ReportEntryFact'):
    self.facts.append(fact)

class ReportEntryFact:
  subpath: str
  label: str
  description: str
  value: any

  def __init__(self, label: str, description: str, value: any, subpath: str = ""):
    self.subpath = subpath
    self.label = label
    self.description = description
    self.value = value

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
    if len(self.report.findings) > 0:
      print("All findings:")
      for finding in self.report.findings:
        print(f"  {finding.path}")
        print(f"    checker: {finding.checker}")
        print(f"    meta: {finding.meta}")
        for fact in finding.facts:
          print(f"    {fact.subpath} {fact.label}: {fact.value}")

class ReportYamlExport:

  def __init__(self, report: Report):
    self.report = report

  def export(self, path: str):
    data = {}

    # add missing files
    if len(self.report.files_missing) > 0:
      data["missing_files"] = self.report.files_missing

    # add extra files
    if len(self.report.files_extra) > 0:
      data["extra_files"] = self.report.files_extra

    # add all findings
    if len(self.report.findings) > 0:
      data["checked_files"] = []
      for finding in self.report.findings:
        item = {}
        item["path"] = finding.path
        item["checker"] = finding.checker
        #item["meta"] = finding.meta
        item["findings"] = []
        for fact in finding.facts:
          fact_item = {}
          fact_item["subpath"] = fact.subpath
          fact_item["label"] = fact.label
          fact_item["description"] = fact.description
          fact_item["value"] = fact.value
          item["findings"].append(fact_item)
        data["checked_files"].append(item)
  
    # write yaml file
    with open(path, "w") as f:
      yaml.dump(data, f)