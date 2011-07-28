import re
from bitstring import ConstBitArray

def to_words(text):
    return text.split()

def take_char_input(stream):
    return stream.read()

def take_binary_input(stream):
    return ConstBitArray(bytes=stream.read())

def to_phrases(order, words):
    return [tuple([words[i+j] for j in xrange(order+1)])
            for i in xrange(len(words) - order)]
