'''
Copyright:   (c) Geometric 2015
Purpose: Tests for cdd
'''
import unittest
import code_duplication_extractor as dups_extractor
import optparse

class Options: pass

def inject_parse_args():
    options = Options()
    args = []

    options.format = 'txt'
    options.lang = 'py'
    options.outfile = './testdata/outfile'
    options.pattern = ""
    options.log = False
    options.report = None
    options.minimum = 100
    options.fuzzy = False
    options.min_lines = 3
    options.blame = False

    args.append('./testdata')

    return options,args

class TestFixture(unittest.TestCase):
    def setUp(self):
        mock_parser = optparse.OptionParser("", description="")
        mock_parser.parse_args = inject_parse_args
        dups_extractor.get_option_parser = lambda : mock_parser

    def test_on_cooked_up_python_files_containing_duplicates(self):
        dups = dups_extractor.extract_duplicates()
        expected = {1: {'linecount': 37, 'fcount': 2}, 2: {'linecount': 30, 'fcount': 2},
                    3: {'fcount': 2,'linecount': 20}, 4: {'linecount': 18, 'fcount': 3}}
        self.assertEqual(expected,dups)





if __name__=='__main__':
    unittest.main()