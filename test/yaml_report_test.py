import unittest, math, random, sys, os, json, yaml, shutil
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.main import compare
from src.Report import Report, ReportConsolePrint, ReportYamlExport

TEMP_DIR = 'tmp'

def create_file(base: str, path: str, src_content: any, ref_content: any):
  ext = os.path.splitext(path)[1]

  src_path = os.path.join(base, 'src', path)
  ref_path = os.path.join(base, 'ref', path)

  # create directories
  os.makedirs(os.path.dirname(src_path), exist_ok=True)
  os.makedirs(os.path.dirname(ref_path), exist_ok=True)

  # create files
  if ext == '.json':
    assert isinstance(src_content, dict) or src_content is None
    assert isinstance(ref_content, dict) or ref_content is None

    if src_content is not None:
      with open(src_path, 'w') as f: 
        json.dump(src_content, f, indent=2)
    
    if ref_content is not None:
      with open(ref_path, 'w') as f: 
        json.dump(ref_content, f, indent=2)
  
  elif ext in ['.yml', '.yaml']:
    assert isinstance(src_content, dict) or src_content is None
    assert isinstance(ref_content, dict) or ref_content is None

    if src_content is not None:
      with open(src_path, 'w') as f:
        yaml.dump(src_content, f, indent=2)

    if ref_content is not None:
      with open(ref_path, 'w') as f:
        yaml.dump(ref_content, f, indent=2)

  elif ext in ['.txt', '.md']:
    assert isinstance(src_content, str) or src_content is None
    assert isinstance(ref_content, str) or ref_content is None

    if src_content is not None:
      with open(src_path, 'w') as f:
        f.write(src_content)

    if ref_content is not None:
      with open(ref_path, 'w') as f:
        f.write(ref_content)

  elif ext == '.nrrd' or path[:-7] == '.nii.gz':
    assert isinstance(src_content, str) or src_content is None
    assert isinstance(ref_content, str) or ref_content is None

    if src_content.startswith('http') and ref_content.startswith('http'):
      if src_content is not None:
        download_file(path, src_content)
      if ref_content is not None:
        download_file(path, ref_content)
    elif src_content.startswith('/') and ref_content.startswith('/'):
      if src_content is not None:
        copy_file(src_content, path)
      if ref_content is not None:
        copy_file(ref_content, path)
    else:
      raise Exception("Unsupported content")
  else:
    raise Exception("Unsupported file type: " + ext)

def download_file(path: str, url: str):
  pass

def copy_file(src: str, dst: str):
  pass


class ReportPassingTest(unittest.TestCase):

  def setUp(self):
    random.seed(823468228)

    # create temporary structure
    self.base = os.path.join(TEMP_DIR, self.__class__.__name__)
    
    # create temporary structure
    create_file(self.base, 'data.yml', {'a': 1, 'b': 2.00}, {'a': 1, 'b': 2.0})
    create_file(self.base, 'deep/data.json', {'a': 1, 'b': 2}, {'a': 1, 'b': 2})
    create_file(self.base, 'README.md', 'Hello World', 'Hello World')
    create_file(self.base, 'deep/nested/data.txt', 'Hello World\nThere is more', 'Hello World\nThere is more')
    
  def tearDown(self) -> None:
    shutil.rmtree(self.base)

  def test_report(self):
    src_path = os.path.join(self.base, 'src')
    ref_path = os.path.join(self.base, 'ref')

    # compare
    report = compare(src_path, ref_path)

    # validate report
    ReportConsolePrint(report).print()

    # yml report
    #ReportYamlExport(report).export(self.__class__.__name__ + '.report.yml')
    report_yml_data = ReportYamlExport(report).generate()

    # checks
    self.assertFalse('missing_files' in report_yml_data)
    self.assertFalse('extra_files' in report_yml_data)
    self.assertEqual(len(report_yml_data['checked_files']), 6)

    # summary
    self.assertEqual(report_yml_data['summary']['files_missing'], 0)
    self.assertEqual(report_yml_data['summary']['files_extra'], 0)
    self.assertEqual(report_yml_data['summary']['checks']['DataFileCheck']['files'], 2)
    self.assertFalse('findings' in report_yml_data['summary']['checks']['DataFileCheck'])
    self.assertEqual(report_yml_data['summary']['checks']['SizeCheck']['files'], 4)
    self.assertFalse('findings' in report_yml_data['summary']['checks']['SizeCheck'])

    # conclusion
    self.assertTrue(report_yml_data['conclusion'])


class ReportDeviationTest(unittest.TestCase):

  def setUp(self):
    random.seed(823468228)
    
    self.base = os.path.join(TEMP_DIR, self.__class__.__name__)

    # create temporary structure
    create_file(self.base, 'data.yml', {'a': 1, 'b': 2.00000}, {'a': 1, 'b': 2.00008})
    create_file(self.base, 'deep/data.json', {'a': 1, 'deep': [{'b': 2, 'd': 3}]}, {'a': 1, 'deep': [{'b': 2, 'c': 3}]})
    create_file(self.base, 'README.md', 'Hello World', 'Hello World')
    create_file(self.base, 'deep/nested/data.txt', 'Hello World', 'Hello World\nThere is more')
    create_file(self.base, 'deep/nested/missing.yml', None, {'a': 1, 'b': 2})
    create_file(self.base, 'deep/nested/extra.yml', {'a': 1, 'b': 2}, None)
    
  def tearDown(self) -> None:
    shutil.rmtree(self.base)

  def test_report(self):
    src_path = os.path.join(self.base, 'src')
    ref_path = os.path.join(self.base, 'ref')

    # compare
    report = compare(src_path, ref_path)

    # validate report
    ReportConsolePrint(report).print()

    # yml report
    #ReportYamlExport(report).export(self.__class__.__name__ + '.report.yml')
    report_yml_data = ReportYamlExport(report).generate()

    # checks
    self.assertListEqual(report_yml_data['missing_files'], ['deep/nested/missing.yml'])
    self.assertListEqual(report_yml_data['extra_files'], ['deep/nested/extra.yml'])
    self.assertEqual(len(report_yml_data['checked_files']), 4)

    # summary
    self.assertEqual(report_yml_data['summary']['files_missing'], 1)
    self.assertEqual(report_yml_data['summary']['files_extra'], 1)
    self.assertEqual(report_yml_data['summary']['checks']['DataFileCheck']['files'], 2)
    self.assertDictEqual(report_yml_data['summary']['checks']['DataFileCheck']['findings'], {
      'Value similar': 1,
      'Extra key': 1,
      'Missing key': 1
    })
    self.assertEqual(report_yml_data['summary']['checks']['SizeCheck']['files'], 4)
    self.assertDictEqual(report_yml_data['summary']['checks']['SizeCheck']['findings'], {
      'Size Difference': 2
    })

    # conclusion
    self.assertFalse(report_yml_data['conclusion'])
