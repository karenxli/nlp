# imports go here
import random
import bisect
import collections
import statistics as st


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
    self.vocab = 0

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

  # calculates the probability of a sentence using unigram model
  def uni_probability(self, sentence):
    if(self.smooth):
      denominator = len(self.corpus) + self.vocab
    else:
      denominator = len(self.corpus)

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

  # calculates the probability of a sentence using bigram model
  def biProbability(self, sentence):
    prob = 1
    previousWord = None
    for word in sentence:
      if previousWord != None:
        bigramProb = self.biWord(previousWord, word)
        prob = bigramProb * prob
      previousWord = word
    return prob

 # calculates the probability of a word in a bigram model, given the previous word
  def biWord(self, prev, word):
    # probability is # of times the n-gram prev, word comes up
    # divided by the number of times an n-gram with prev shows up at all
    temp_corpus = self.corpus.copy()

    if(sum(prev in s for s in self.corpus) == 0) : prev = self.UNK
    if(sum(word in s for s in self.corpus) == 0) : word = self.UNK

    denominator = 0
    for term in temp_corpus:
      if(term.split()[0] == prev):
        denominator += 1
    numerator = self.unigram_frequencies[str(prev) + ' ' + str(word)]

    if self.smooth:
        numerator += 1
        denominator += self.vocab
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
        self.corpus = [self.UNK if word == item else item for item in self.corpus]

    self.vocab = len(set(self.corpus))
    # step 3 is done 
    self.corpus = self.ngramMaker(self.corpus, self.gramCount)
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
    if(self.gramCount == 1):
      total_prob = self.uni_probability(sent_text)
    else:
      return self.biProbability(sent_text)
 
    for x in total_prob:
        sent_prob *= x
    return sent_prob

    # this score can be very very small

  # generates an individual sentence based on an unigram or bigram model
  # wrapper for generate_unigram and generate_bigram
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

  # generates a sentence for a bigram model
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
      newWord = self.findInterval(probability, randNum) # random number generator

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
  # TODO: ngl i have no idea how this works and the deliverables just say "turn in your curated set of words"
  #training_path = sys.argv[1]
  #testing_path1 = sys.argv[2]
  #testing_path2 = sys.argv[3]
  

  f = open("hw2-my-test.txt", "r")
  whitman = [line.rstrip('\n') for line in f]
  f.close()
  
  # Unigram model
  print("Unigram model")
  print("No of sentences: 50")
  lm = LanguageModel(1, True)
  lm.train("hw2-my-test.txt")
  uniscores = []
  for n in whitman:
    uniscores.append(lm.score(n))
  
  print("Average probability = " + str(sum(uniscores)/len(uniscores)))
  print("Standard deviation = " + str(st.stdev(uniscores)))
  print("Sentences:")
  print(lm.generate(50))

  print(" ")

  # Bigram model
  print("Bigram model")
  print("No of sentences: 50")
  biscores = []
  bi = LanguageModel(2, True)
  bi.train("hw2-my-test.txt")
  for a in whitman:
    biscores.append(bi.score(a))

  print("Average probability = " + str(sum(biscores)/len(biscores)))
  print("Standard deviation = " + str(st.stdev(biscores)))
  print("Sentences:")
  print(bi.generate(50))

  

    
if __name__ == '__main__':
    
  # make sure that they've passed the correct number of command line arguments
  #if len(sys.argv) != 4:
  # print("Usage:", "python lm.py training_file.txt hw2-my-test.txt training_files/hw2-test.txt")
  # sys.exit(1)

  main()
