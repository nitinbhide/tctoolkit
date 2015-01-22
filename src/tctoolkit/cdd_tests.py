'''
Purpose: Tests for cdd
'''
import unittest
import code_duplication_extractor as dups_extractor
import optparse


class TestFixture(unittest.TestCase):
#[manojp: 22/01/2015]: test for duplicates across files needs to be corrected.
    def test_on_cooked_up_python_files_containing_duplicates(self):
        dups = dups_extractor.extract_duplicates(lang='py',srclocation='.\\testdata')

        analytics_data = dups.pop('analytics')
        analytics = {'analytics': analytics_data}

        dups_expected = {1: {'linecount': 37, 'fcount': 2}, 2: {'linecount': 30, 'fcount': 2},
                    3: {'fcount': 2,'linecount': 20}, 4: {'linecount': 18, 'fcount': 3}}
        self.assertEqual(dups_expected,dups)

        analytics_expected = {'num_dups': 4, 'num_dups_across_files':4,
                              'dups_loc': (37+30+20+(18*2))}
        self.assertEqual(analytics_expected,analytics['analytics'])


    def test_that_higher_level_analytics_data_is_computed_correctly(self):
        dups = {1: {'linecount': 20, 'fcount': 2}, 2: {'linecount': 30, 'fcount': 5}}

        dups_analytics = dups_extractor.extract_dups_analytics(dups)
        expected = {'num_dups': 2, 'num_dups_across_files':2,
                              'dups_loc': (20+(30*4))}
        self.assertEqual(expected,dups_analytics['analytics'])



if __name__=='__main__':
    unittest.main()