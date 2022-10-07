# imports go here
from lib2to3.pgen2.tokenize import tokenize
import sys
import math
import re
import collections

"""
Karen Li

CS 4120 NLP HW #2
"""


# Feel free to implement helper functions


class LanguageModel:
  # constants to define pseudo-word tokens
  # access via self.UNK, for instance
  UNK = "<UNK>"
  SENT_BEGIN = "<s>"
  SENT_END = "</s>"

  def __init__(self, n_gram, is_laplace_smoothing):
    """Initializes an untrained LanguageModel
    Parameters:
      n_gram (int): the n-gram order of the language model to create
      is_laplace_smoothing (bool): whether or not to use Laplace smoothing
    """
    self.gramCount= n_gram                              # type of n_gram
    self.smooth = is_laplace_smoothing                  # laplace smoothing?
    self.unigram_frequencies = collections.Counter()    # unigram frequencies
    self.corpus = []                                    # the unigrams themselves

  # populates the frequency list per article
  def count(self, article):

    frequency = collections.Counter()
    for word in article:
        frequency[word] = frequency.get(word, 0) + 1
        #self.unigram_frequencies[word] = self.unigram_frequencies.get(word, 0) + 1
    return frequency
  # tokenizes a given txt file
  def splitText(self, training_file_path):
    f = open(training_file_path, "r")
    text = f.read().split()
    f.close()
    return text

 # calculates the probabilities of all elements in a single sentence
 # returns a list of that sentence's probabilities
  def probability(self, sentence):
    count = 0
    for m in self.unigram_frequencies:
        count = count + self.unigram_frequencies[m]
    #count is now the total of all values - make this a general constant?

    prob = []
    for word in sentence:
        if(self.corpus.count(word) == 0 
            and self.unigram_frequencies[self.UNK] > 0):
                prob.append(self.unigram_frequencies[self.UNK]/count)
        else: 
            prob.append(self.unigram_frequencies[word]/count)
    return prob


  # creates ngrams
  def ngramMaker(self, training_file_path, gramCount):
    text = self.splitText(training_file_path) #tokenizes
 
    ngrams = zip(*[text[i:] for i in range(gramCount)])
    return [" ".join(ngram) for ngram in ngrams]


  def train(self, training_file_path):
    """Trains the language model on the given data. Assumes that the given data
    has tokens that are white-space separated, has one sentence per line, and
    that the sentences begin with <s> and end with </s>
    Parameters:
      training_file_path (str): the location of the training data to read

    Returns:
    None
    """
    self.corpus = self.splitText(training_file_path) #tokenizes
    uncleaned = self.count(self.corpus) # does an initial count of all words

    # FIX THIS BIT
    self.corpus = self.ngramMaker(training_file_path, self.gramCount)
    unknowns = []
    for num in uncleaned: # finds all the single words 
        if uncleaned[num] == 1:
            unknowns.append(num)
    
    for word in unknowns:
        self.corpus = [t.replace(word, self.UNK) for t in self.corpus]
        #del self.unigram_frequencies[word]
    self.unigram_frequencies = self.count(self.corpus)



  def score(self, sentence):
    """Calculates the probability score for a given string representing a single sentence.
    Parameters:
      sentence (str): a sentence with tokens separated by whitespace to calculate the score of
      
    Returns:
      float: the probability value of the given string for this model
    """
    sent_prob = 1

    sent_text = sentence.split()
    total_prob = self.probability(sent_text)
 
    for x in total_prob:
        sent_prob *= x
    return sent_prob

    # this score can be very very small
  def generate_sentence(self):
    """Generates a single sentence from a trained language model using the Shannon technique.
      
    Returns:
      str: the generated sentence
    """
    pass

  def generate(self, n):
    """Generates n sentences from a trained language model using the Shannon technique.
    Parameters:
      n (int): the number of sentences to generate
      
    Returns:
      list: a list containing strings, one per generated sentence
    """
    pass
    


def main():
  # TODO: implement
  training_path = sys.argv[1]
  testing_path1 = sys.argv[2]
  testing_path2 = sys.argv[3]
  
  pass

    
if __name__ == '__main__':
    
  # make sure that they've passed the correct number of command line arguments
  if len(sys.argv) != 4:
    print("Usage:", "python hw2_lm.py training_file.txt testingfile1.txt testingfile2.txt")
    sys.exit(1)

  main()
