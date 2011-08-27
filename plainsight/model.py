import sys
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
        #print 'moving to ROOT'
        self.move_to_root()
        for token in tokens:
         #  print 'moving to token %s' % token
            self.move_to_child(token)

    def get_children(self):
        return self.pointer[1]

    def get_child_tokens(self):
        phrases = map(lambda x: x[0], self.get_children().items())
        return phrases

    def top(self, limit):
        # already sorted, thanks to call to model.sort_all_children()
        top_phrases = self.get_counts()

        # collect all phrases that occur in the top part of the
        # probability mass:
        return top_phrases[:limit]

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
# next_output: get the next bits, or tokens, to output

def next_output(payload, enum, mode, limit):
    choices = len(enum)
    if choices <= 1:
        return None, 0
    choices = min(choices, limit)
    choice_bits = probability.len_log2_floor(choices)
    # if there are no choices, return None:
    if choice_bits == 0: return None, 0

    if mode == 'encipher':
        bits_to_take = choice_bits#min(len(payload), choice_bits)
    if mode == 'decipher':
        token = payload[0]

    if mode == 'encipher':
        bits = payload[:bits_to_take]
        return bits.uint, bits_to_take
    elif mode == 'decipher':
        # payload is token array

        if len(payload) == 0: return None, 0

        if token in enum:
            ind = enum.index(token)
            bits = ConstBitArray(uint=ind, length=choice_bits)
            return token, bits
        else:
            return None, 0
###############################################################################
# cipher: encipher or decipher input, given a linguistic model

def cipher(model, order, payload, mode, limit_max=None):
    if mode == 'encipher': output = []
    if mode == 'decipher': output = BitArray()
    context = []
    initial_length = len(payload)
    pbar = ProgressBar(widgets=['%sing: ' % mode,
                                Percentage(),
                                Bar(),
                                FileTransferSpeed(),
                                ' | ',
                                ETA()],
                                maxval=initial_length or 1).start()
    bit_marker = 0
    payload_remaining = initial_length
    while payload_remaining > 0:
        model.abs_move_to_child(context) # reset context
        #print 'moving to: %s' % context
        if mode == 'encipher' and payload_remaining < 8:
            limit = 2**(8 - bit_marker)
        elif mode == 'decipher' and payload_remaining == 1:
            limit = 2**(8 - bit_marker)
        else:
            if limit_max is None:
                limit = 2**32
            else:
                limit = limit_max
        top_tokens = model.top(limit) # get tokens for conversion
        if mode == 'encipher':
            index, nBits = next_output(payload, top_tokens, 'encipher',
                                      limit)
                                      # payload[0] == 0)
                                       #False)#payload_remaining < 3)
            bits = None
            if index is not None:
                token = top_tokens[index]
                context.append(token)
        if mode == 'decipher':
            token, bits = next_output(payload, top_tokens, 'decipher',
                                      limit)
                                      #False)#payload_remaining < 3)
            if token is not None:
                nBits = len(bits)
                index = top_tokens.index(token)
                context.append(token)

        if mode == 'encipher' and index is not None and nBits > 0:
            token = top_tokens[index]
            payload = payload[nBits:]
            output.append(token)
            payload_remaining -= nBits
            bit_marker += nBits
            bit_marker = bit_marker % 8
        elif mode == 'encipher' and len(model.get_children()) == 1:
            # there is no information conveyed when there is no choice to make.
            # this means that no input bits are consumed. it is purely for
            # appearances that you can choose to leave these default tokens, or
            # not. leaving them in seems to make the text more human-like.
            token = model.get_child_tokens()[0]
            context.append(token)
            context = context[1:] # back up the context
        elif mode == 'encipher':
            context = context[1:] # back up the context
        elif mode == 'decipher' and token is not None and len(bits) > 0:
            payload = payload[1:]
            output.append(bits)
            bit_marker += len(bits)
            bit_marker = bit_marker % 8
            payload_remaining -= 1
        elif mode == 'decipher' and len(model.get_child_tokens()) == 1:
            if mode == 'decipher':
                if mode == 'decipher':
                    token = model.get_child_tokens()[0]
                context.append(token)
                context = context[1:] # remove context to find tokens
        elif mode == 'decipher':
            context = context[1:] # remove context to find tokens
        pbar.update(initial_length - payload_remaining)
    pbar.finish()
    if mode == 'encipher': return ' '.join(output)
    if mode == 'decipher': return output

