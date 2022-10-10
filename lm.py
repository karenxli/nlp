# imports go here
from lib2to3.pgen2.tokenize import tokenize
import sys
import random
import bisect
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
    self.path = ""

  # populates the frequency list per article
  def count(self, article):

    frequency = collections.Counter()
    for word in article:
        frequency[word] = frequency.get(word, 0) + 1
        
    return frequency
  # tokenizes a given txt file
  def splitText(self, training_file_path):
    f = open(training_file_path, "r")
    text = f.read().split()
    f.close()
    return text


  def uni_probability(self, sentence):
    if(self.smooth):
      denominator = len(self.corpus) + len(set(self.corpus))
    else:
      denominator = len(self.corpus)
    print(self.corpus)

    #count is now the total of all values - make this a general constant?

    prob = []
    for word in sentence:
        if(self.corpus.count(word) == 0 
            and self.unigram_frequencies[self.UNK] > 0): # if the word itself doesn't exist, use UNK values
                numerator = self.unigram_frequencies[self.UNK]
                if(self.smooth):
                  numerator = numerator + 1 # laplace smoothing
                prob.append(numerator/denominator)
        else: 
            numerator = self.unigram_frequencies[word]
            if(self.smooth):
                  numerator = numerator + 1
            prob.append(numerator/denominator)
    return prob

  def biProbability(self, sentence):
    prob = 1
    previousWord = None
    for word in sentence:
      if previousWord != None:
        bigramProb = self.biWord(previousWord, word)
        prob = bigramProb * prob
      previousWord = word
    return prob

  def biWord(self, prev, word):
    temp_corpus = self.splitText(self.path)
    smoothing = len(set(temp_corpus))

    denominator = temp_corpus.count(prev)
    numerator = self.unigram_frequencies[str(prev) + ' ' + str(word)]

    if self.smooth:
        numerator += 1
        denominator = denominator + smoothing
    return 0.0 if numerator == 0 or denominator == 0 else float(
            numerator) / float(denominator)
  
  # creates ngrams
  def ngramMaker(self, splittedText, gramCount):
 
    ngrams = zip(*[splittedText[i:] for i in range(gramCount)])
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

    # tokenize, count, change into unknowns, split, then count again
    self.path = training_file_path
    self.corpus = self.splitText(training_file_path)
    uncleaned = self.count(self.corpus) # does an initial count of all words
    unknowns = []
    for num in uncleaned: # finds all the single words 
        if uncleaned[num] == 1:
            unknowns.append(num)
    
    for word in unknowns:
        self.corpus = [t.replace(word, self.UNK) for t in self.corpus]

    # step 3 is done 
    self.corpus = self.ngramMaker(self.corpus, self.gramCount)
    self.unigram_frequencies = self.count(self.corpus)
   
    #print(self.corpus)
    #print(self.unigram_frequencies)


  def score(self, sentence):
    """Calculates the probability score for a given string representing a single sentence.
    Parameters:
      sentence (str): a sentence with tokens separated by whitespace to calculate the score of
      
    Returns:
      float: the probability value of the given string for this model
    """
    sent_prob = 1

    sent_text = sentence.split()
    if(self.gramCount == 1):
      total_prob = self.uni_probability(sent_text)
    else:
      return self.biProbability(sent_text)
 
    for x in total_prob:
        sent_prob *= x
    return sent_prob

    # this score can be very very small

  def generate_sentence(self):
    """Generates a single sentence from a trained language model using the Shannon technique.
      
    Returns:
      str: the generated sentence
    """
    # returns a string
    if(self.gramCount == 1):
      sentence = self.generate_unigram()
    else:
      sentence = self.generate_bigram()

    return sentence


  # generates a sentence for unigrams
  def generate_unigram(self):
    '''
    get probabilities for the freq
    sort them highest to lowest
    change probabilities to be a full thing
    send to gen sentence
    '''

    spectrum = self.unigram_frequencies.copy()
    del spectrum[self.SENT_BEGIN]
    denom = 0
    for m in spectrum:
        denom = denom + spectrum[m]
    for word in spectrum:
      spectrum[word] = spectrum[word]/denom

    spectrum = spectrum.most_common()
    spectrum = [list(spect) for spect in spectrum]

    rolling_prob = 0
    for word in spectrum:
      word[1] += rolling_prob
      rolling_prob = word[1] # reassign to the running total 


    sentence = self.SENT_BEGIN
    new_word = ""
    while(new_word != self.SENT_END):
      randNum = random.uniform(0, 1)
      new_word = self.findInterval(spectrum, randNum)
      
      sentence += " " + new_word 
    return sentence

  # generates a sentence for
  def generate_bigram(self):
    '''
    - for starting word: grab all unigrams with it
    '''
    sentence = self.SENT_BEGIN
    prevWord = self.SENT_BEGIN
    newWord = ""
    spectrum = self.corpus.copy()

    while(prevWord != self.SENT_END):
      prevCorpus = []
      for word in spectrum:
        if(word.split()[0] == prevWord):
          prevCorpus.append(word)

      probability = self.probabilityFinder(prevCorpus)

      randNum = random.uniform(0, 1)
      newWord = self.findInterval(probability, randNum)

      sentence += " " + newWord
      prevWord = newWord


    return sentence
    
  # does probability pre-processing for bigram models
  def probabilityFinder(self, newCorp):
    words = self.count(newCorp).most_common()
    words = [list(spect) for spect in words]
    denom = 0
    for m in words:
        denom = denom + m[1]
    for word in words:
      word[1] = word[1]/denom

    rolling_prob = 0
    for word in words:
      word[1] += rolling_prob
      rolling_prob = word[1] # reassign to the running total 
    return words

  # finds the word that the random value falls to
  def findInterval(self, spect, val):

    inter = bisect.bisect_left(list(dict(spect).values()), val)
    if(self.gramCount == 1):
        return spect[inter][0]
    else:
      result = spect[inter][0].split()[1]
      return result

  def generate(self, n):
    """Generates n sentences from a trained language model using the Shannon technique.
    Parameters:
      n (int): the number of sentences to generate
      
    Returns:
      list: a list containing strings, one per generated sentence
    """
    paragraph = []
    for i in range(n):
      paragraph.append(self.generate_sentence())
    return paragraph

    


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
