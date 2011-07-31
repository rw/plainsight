from math import floor, log
from time import clock, time

from bitstring import BitArray, ConstBitArray
from progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar

import data, probability

###############################################################################
# A Model contains frequency counts and probabiliteis of n-grams extracted
# from at least one source text. The source text is tokenized, then fed into
# the Model one n-length slice at a time.
#
# Each node has the format:
# [occurrence count, children, tokens to use in conversion (lazily computed)]
#
###############################################################################

class Model:
    def __init__(self, context):
        self.context = context
        self._children = [0, {}, None]
        self.current_token = None
        self.pointer = self._children

    def add_phrase(self, p):
        ptr = self._children[1]
        for token in p:
            if token not in ptr:
               ptr[token] = [0, {}, None]

            ptr[token][0] += 1
            ptr = ptr[token][1]

    def update_root_count(self):
        tokens = self._children[1].values()
        total = sum(map(lambda t: t[0], tokens))
        self._children[0] = total

    def current_count(self):
        return self.pointer[0]

    def move_to_root(self):
        self.pointer = self._children
        self.current_token = None

    # start from current node
    def move_to_child(self, token):
        self.pointer = self.pointer[1][token]
        self.current_token = token

    # start from root
    def abs_move_to_child(self, tokens):
        self.move_to_root()
        for token in tokens:
            self.move_to_child(token)

    def get_children(self):
        return self.pointer[1]

    def get_child_tokens(self):
        phrases = map(lambda x: x[0], self.get_children().items())
        return phrases

    def top(self):
        # already sorted, thanks to call to model.sort_all_children()
        top_phrases = self.get_counts()

        # collect all phrases that occur in the top part of the
        # probability mass:
        return top_phrases

    def update_counts(self):
        # sort tokens on this branch by their frequency
        sorted_phrases = sorted(self.get_children().items(),
                                reverse=True,
                                key=lambda x: x[1][0])

        # do the statistics judo:
        mass, current = 0.5, 0.0

        # probability mass to select, by frequency
        limit = floor(self.current_count() * mass)

        # since probability mass is (currently) a constant, store these too:
        t = []
        for p in sorted_phrases:
            if current + p[1][0] < limit:
                current += p[1][0]
                t.append(p[0])
            else:
                break
        self.pointer[2] = t

    def get_counts(self):
        if self.pointer[2] is None:
            self.update_counts()
        return self.pointer[2]

    def add_text(self, text, context):
        phrases = data.to_phrases(context, data.to_words(text))
        for p in phrases:
            self.add_phrase(p)
        self.update_root_count()

###############################################################################
# utility methods for ciphering
# TODO: merge next_index and next_token (they share most code)

# for encipher
def next_index(in_bits, enum):
    choices = len(enum)

    if choices <= 1:
        return None, 0
    choice_bits = probability.len_log2_floor(choices)
    nBits = len(in_bits)

    # if there are no choices, return None:
    if choice_bits == 0: return None, 0

    bits_to_take = min(choice_bits, nBits)
    bits = in_bits[:bits_to_take]
    return bits.uint, bits_to_take

# for decipher
def next_token(in_ciphertext, enum):
    choices = len(enum)

    if choices <= 1:
        return None, 0
    choice_bits = probability.len_log2_floor(choices)

    # if there are no choices, return None:
    if choice_bits == 0: return None, 0
    if len(in_ciphertext) == 0: return None, 0

    tok = in_ciphertext[0]
    if tok in enum:
        ind = enum.index(tok)
        bits = ConstBitArray(uint=ind, length=choice_bits)
        return tok, bits
    else:
        return None, 0

###############################################################################
# main encipher method

def encipher(model, order, cleartext):
    ciphertext, context = [], []
    input_length, bits_processed = len(cleartext), 0
    initial_length = input_length
    pbar = ProgressBar(widgets=['enciphering: ', Percentage(), Bar(), FileTransferSpeed(),
                                ' | ', ETA()], maxval=initial_length).start()
    while (initial_length - bits_processed) > 0:
        model.abs_move_to_child(context) # reset context
        top_tokens = model.top() # get tokens for conversion
        index, nBits = next_index(cleartext, top_tokens)
        if index is not None and nBits > 0:
            token = top_tokens[index]
            cleartext = cleartext[nBits:]
            ciphertext.append(token)
            context.append(token)
        elif len(model.get_children()) == 1:
            # there is no information conveyed when there is no choice to make.
            # this means that no input bits are consumed. it is purely for
            # appearances that you can choose to leave these default tokens, or
            # not. leaving them in seems to make the text more human-like.
            token = model.get_child_tokens()[0]
            context.append(token)
            context = context[1:] # back up the context
        else:
            context = context[1:] # back up the context
        bits_processed += nBits
        pbar.update(initial_length - bits_processed)
    pbar.finish()
    return ' '.join(ciphertext)

###############################################################################
# main decipher method

def decipher(model, order, ciphertext):
    cleartext, context = BitArray(), []
    tokens_processed = 0
    initial_length = len(ciphertext)
    pbar = ProgressBar(widgets=['deciphering: ', Percentage(), Bar(), FileTransferSpeed(),
                                ' | ', ETA()], maxval=initial_length).start()
    while (initial_length - tokens_processed) > 0:
        model.abs_move_to_child(context)
        top_tokens = model.top()
        token, bits = next_token(ciphertext, top_tokens)
        if token is not None and len(bits) > 0:
            ciphertext = ciphertext[1:]
            cleartext.append(bits)
            context.append(token)
            tokens_processed += 1
        elif len(model.get_child_tokens()) == 1:
            token = model.get_child_tokens()[0]
            context.append(token)
            context = context[1:] # remove context to find tokens
        else:
            context = context[1:] # remove context to find tokens
        pbar.update(tokens_processed)
    pbar.finish()
    return cleartext