import unittest, sys
sys.path.append('..')
from loc import Countlines
#java 10
#c++ 5
#python 7
#csharp 70
class Test(unittest.TestCase):
    def test_loc(self):
        lang ,dirname= input().split()
        app = Countlines(lang, dirname)
        self.assertEqual(app.run(dirname), 64)
if __name__ == '__main__':
    unittest.main()