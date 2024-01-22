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

    # print different files
    # if len(self.report.files_different) > 0:
    #   print("Files different from reference:")
    #   for diff_path in self.report.files_different:
    #     print(f"  {diff_path}")

    # print details about different files
    # if len(self.report.files_different) > 0:
    #   print("Details about files different from reference:")
    #   for item in self.report.files_different:
    #     print(f"  {item.path}")
    #     print(f"    src: {item.src_value}")
    #     print(f"    ref: {item.ref_value}")
    #     print(f"    outcome: {item.outcome}")
    #     print(f"    precision: {item.precision}")

    # print all findings
    if len(self.report.findings) > 0:
      print("All findings:")
      for finding in self.report.findings:
        print(f"  {finding.path}")
        print(f"    checker: {finding.checker}")
        print(f"    meta: {finding.meta}")
        for fact in finding.facts:
          print(f"    {fact.subpath} {fact.label}: {fact.value}")



  