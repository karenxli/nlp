import unittest
from lm import LanguageModel

class TestMiniTraining(unittest.TestCase):
  
  def test_createunigrammodelnolaplace(self):
    unigram = LanguageModel(1, False)
    self.assertEqual(1, 1, msg="tests constructor for 1, False")

  def test_createunigrammodellaplace(self):
    unigram = LanguageModel(1, True)
    self.assertEqual(1, 1, msg="tests constructor for 1, True")

  def test_createbigrammodelnolaplace(self):
    bigram = LanguageModel(2, False)
    self.assertEqual(1, 1, msg="tests constructor for 2, False")

  def test_createbigrammodellaplace(self):
    bigram = LanguageModel(2, True)
    self.assertEqual(1, 1, msg="tests constructor for 2, True")

  def test_unigramlaplace(self):
    lm = LanguageModel(1, True)
    lm.train("training_files/iamsam.txt")
  
  def test_unigramunknowns(self):
    lm = LanguageModel(1, False)
    lm.train("training_files/unknowns_mixed.txt")

  def test_onlyunknownsgenerationandscoring(self):
    lm = LanguageModel(1, True)
    lm.train("training_files/unknowns.txt")

  def test_berptraining(self):
    lm = LanguageModel(1, True)
    lm.train("training_files/berp-training.txt")
if __name__ == "__main__":
  unittest.main()
