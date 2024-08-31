import unittest
import random
import sys
import os
import shutil
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from medcmp.main import compare
from medcmp.Report import ReportConsolePrint, ReportYamlExport

TEMP_DIR = 'tmp'

class ReportPassingTestForCSV(unittest.TestCase):

  def setUp(self):
    random.seed(823468228)

    # create temporary structure
    self.base = os.path.join(TEMP_DIR, self.__class__.__name__)
    src_path = os.path.join(self.base, 'src')
    ref_path = os.path.join(self.base, 'ref')
    
    # create directories
    os.makedirs(src_path, exist_ok=True)
    os.makedirs(ref_path, exist_ok=True)
    
    # create a csv file with dummy data
    src_data = [
      {'a': 1, 'b': 2.00000},
      {'a': 1, 'b': 2.00001},
      {'a': 1, 'b': 2.00002},
      {'a': 1, 'b': 2.00003}
    ]
    
    #src_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    
    ref_data = [
      {'a': 1, 'b': 2.00000, 'c': 1},
      {'a': 1, 'b': 3.00001, 'c': 2},
      {'a': 1, 'b': 2.00002, 'c': 3},
      {'a': 't', 'b': 2.03, 'c': 4}
    ]
    
    #ref_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
    
    # define paths for csv files
    src_path = os.path.join(self.base, 'src', 'data.csv')
    ref_path = os.path.join(self.base, 'ref', 'data.csv')
    
    # write data to csv files
    pd.DataFrame(src_data).to_csv(src_path, index=False)
    pd.DataFrame(ref_data).to_csv(ref_path, index=False)
    
  def tearDown(self) -> None:
    shutil.rmtree(self.base)
    pass

  def test_report(self):
    src_path = os.path.join(self.base, 'src')
    ref_path = os.path.join(self.base, 'ref')

    # compare
    report = compare(src_path, ref_path)

    # # validate report
    ReportConsolePrint(report).print()

    # yml report
    ReportYamlExport(report).export(self.__class__.__name__ + '.report.yml')
    ReportYamlExport(report).generate()
    
    #report_yml_data = ReportYamlExport(report).generate()

    # # checks
    # self.assertFalse('missing_files' in report_yml_data)
    # self.assertFalse('extra_files' in report_yml_data)
    # self.assertEqual(len(report_yml_data['checked_files']), 6)

    # # summary
    # self.assertEqual(report_yml_data['summary']['files_missing'], 0)
    # self.assertEqual(report_yml_data['summary']['files_extra'], 0)
    # self.assertEqual(report_yml_data['summary']['checks']['DataFileCheck']['files'], 2)
    # self.assertFalse('findings' in report_yml_data['summary']['checks']['DataFileCheck'])
    # self.assertEqual(report_yml_data['summary']['checks']['SizeCheck']['files'], 4)
    # self.assertFalse('findings' in report_yml_data['summary']['checks']['SizeCheck'])

    # # conclusion
    # self.assertTrue(report_yml_data['conclusion'])

