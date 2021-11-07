import unittest

from utils import splitName, mergeSplits

class MergeSplits(unittest.TestCase):
    def test_combining(self):
        input = ["ZZ", "atomic", "guy", "Potato Salad Game", "Look at my Song", "DoD"]
        combineString = "0 1,2 3 4 5"
        mergeCharacter = "-"
        expect = ["ZZ", "atomic-guy", "Potato Salad Game", "Look at my Song", "DoD"]
        self.assertEqual(expect, mergeSplits(input, combineString, mergeCharacter))
    def test_combining2(self):
        input = ["05", "Prince of Darkness", "F", "Zero", "Challaball ding", "aling", "DoD"]
        combineString = "0 1 2,3 4,5 6"
        mergeCharacter = "-"
        expect = ["05", "Prince of Darkness", "F-Zero", "Challaball ding-aling", "DoD"]
        self.assertEqual(expect, mergeSplits(input, combineString, mergeCharacter))

if __name__ == '__main__':
    unittest.main()
