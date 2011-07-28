#!/usr/bin/env python -u
import argparse, logging, sys, textwrap
from time import clock, time

import data, probability
from model import *

###############################################################################
# Argument parser

parser = argparse.ArgumentParser(description='Plainsight: a textual steganography to make your data look like prose.',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=textwrap.dedent('''\
                                         Example invocations:
                                         echo "the meeting place is Union Square at 5pm" | ./plainsight.py --mode=encipher -f a-book.txt
                                         '''))
parser.add_argument('-m', '--mode', metavar='MODE', type=str, nargs=1, required=True,
                    choices=['encipher', 'decipher'],
                   help='Operating mode. Valid options are: encipher, decipher.')
parser.add_argument('-c', '--context', metavar='N', type=int, nargs='?', default=3, choices=xrange(11),
                   help='The number of tokens to use as context. ' + \
                        'Choose a number from 0 through 10. Default is 3. ' + \
                        'The time to build a model increases [superlinearly] with this, but so does similarity to the source texts.')
parser.add_argument('-f', '--model-file', metavar='FILE', type=argparse.FileType('rb'), nargs='*',
                   help='One or more files to use when creating the lingustic model. ' + \
                        'The data from the file will be used verbatim. ' + \
                        'Example input: a downloaded a Project Guttenberg book.')
parser.add_argument('-u', '--model-url', metavar='URL', type=str, nargs='*',
                   help='(Not implemented.) One or more URLs to use when creating the lingustic model. ' + \
                        'The data at the URL will be stripped of markup. ' + \
                        'Example input: http://www.gutenberg.org/ebooks/1661.txt.utf8 (Sherlock Holmes).')
#parser.add_argument('-i', '--input', metavar='FILE', type=argparse.FileType('rb'), default=sys.stdin,
#                   help='Input file. Defaults to stdin.')
#parser.add_argument('-o', '--output', metavar='FILE', type=argparse.FileType('wb'), default=sys.stdout,
#                   help='Output file. Defaults to stdout.')
parser.add_argument('-l', '--log', metavar='FILE', type=file, default=sys.stderr,
                   help='Logging file. Defaults to stderr (shows diagnostic data).')

args = parser.parse_args()
MODEL_FILES, MODEL_URLS = args.model_file, args.model_url
MODE = args.mode[0]
CONTEXT = args.context
INPUT, OUTPUT, LOGGING = sys.stdin, sys.stdout, sys.stderr

###############################################################################
# main sequence go

if __name__ == '__main__':
    global_start = time()
    if MODEL_FILES is None and MODEL_URLS is None:
        raise RuntimeError('Provide at least URL or file to build the language model.')

    model = Model(CONTEXT)

    # load files for language model:
    if MODEL_FILES is not None:
        for f in MODEL_FILES:
            start = time()
            model_text = data.take_char_input(f)
            model.add_text(model_text, CONTEXT)
            sys.stderr.write('Model: %s added in %.02fs (context == %d)\n' \
                             % (f.name, time() - start, CONTEXT))

    sys.stderr.write('input is "%s", ' % INPUT.name)
    sys.stderr.write('output is "%s"\n' % OUTPUT.name)

    if MODE == 'encipher':
        cleartext = data.take_binary_input(INPUT)
        ciphertext = encipher(model, CONTEXT, cleartext)
        sys.stdout.write(ciphertext)
    elif MODE == 'decipher':
        ciphertext = data.to_words(data.take_char_input(INPUT))
        cleartext = decipher(model, CONTEXT, ciphertext)
        sys.stdout.write(cleartext.tobytes())
