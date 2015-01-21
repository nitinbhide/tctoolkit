'''
Purpose: Tests for cdd
'''
import unittest
import code_duplication_extractor as dups_extractor
import optparse

class Options:
    def __init__(self):
        self.format = 'txt'
        self.pattern = ""
        self.log = False
        self.report = None
        self.minimum = 100
        self.fuzzy = False
        self.min_lines = 3
        self.blame = False
        self.outfile = ''


def inject_parse_args():
    options = Options()
    options.lang = 'py'
    args = ['./testdata']
    return options,args


class TestFixture(unittest.TestCase):
    def setUp(self):
        mock_parser = optparse.OptionParser()
        mock_parser.parse_args = inject_parse_args
        dups_extractor.get_option_parser = lambda : mock_parser

    def test_on_cooked_up_python_files_containing_duplicates(self):
        dups = dups_extractor.extract_duplicates()
        expected = {1: {'linecount': 37, 'fcount': 2}, 2: {'linecount': 30, 'fcount': 2},
                    3: {'fcount': 2,'linecount': 20}, 4: {'linecount': 18, 'fcount': 3}}
        self.assertEqual(expected,dups)

if __name__=='__main__':
    unittest.main()