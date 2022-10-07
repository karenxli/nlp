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

  
  def test_unigram(self):
    lm = LanguageModel(1, False)
    lm.train("training_files/iamsam2.txt")
    # ((4) / (20))
    self.assertAlmostEqual(.2, lm.score("<s>"), msg="tests probability of <s>, trained on iamsam2.txt")
    # (2 / 20)
    self.assertAlmostEqual(.1, lm.score("sam"), msg="tests probability of sam, trained on iamsam2.txt")
    # (4 / 20) * (2 / 20) * (4 / 20)
    self.assertAlmostEqual(.004, lm.score("<s> ham </s>"), msg="tests probability of <s> ham </s>, trained on iamsam2.txt")

  def test_unigramunknowns(self):
    lm = LanguageModel(1, False)
    lm.train("training_files/unknowns_mixed.txt")
    # ((1) / (11))
    self.assertAlmostEqual(1 / 11, lm.score("flamingo"), places=3, msg="tests probability of flamingo, trained on unknowns_mixed.txt")

  def test_bigramunknowns(self):
    lm = LanguageModel(2, False)
    print(lm.bigram("training_files/unknowns_mixed.txt"))

  

if __name__ == "__main__":
  unittest.main()
