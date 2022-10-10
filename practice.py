import bisect
def findInterval(spect, val):

    inter = bisect.bisect_left(list(dict(spect).values()), val)
    return spect[inter][0]
intervals = [['<s>', 0.2], ['i', 0.4], ['am', 0.6000000000000001], ['</s>', 0.8], ['sam', 0.9], ['ham', 1.0]]
value = 0.37
print(list(dict(intervals).values()))
print(findInterval(intervals, value))