#! /usr/bin/python

import random
import sys
import os

DICT_FILE = "/usr/share/dict/words"

def err(msg):
    sys.stderr.write(msg)
    exit(-1)

def gen_word(d, size):
    result = ""

    offset = random.randint(0, size)
    d.seek(offset)
    byte = d.read(1)
    while byte != '\n':
        byte = d.read(1)

    result = ""

    byte = d.read(1)
    while byte != '\n':
        result += byte
        byte = d.read(1)

    return result

def gen_words(count):
    size = os.path.getsize(DICT_FILE)
    d = open(DICT_FILE, 'r')

    while count > 0:
        word = gen_word(d, size)
        if len(word) >= 4 and len(word) <= 8:
            print word
            count -= 1

def main():

    if len(sys.argv) > 2:
        err("usage: " + sys.argv[0] + " [COUNT]\n")

    if len(sys.argv) == 2:
        count = sys.argv[1]
    else:
        count = 1

    gen_words(int(count))

if __name__ == "__main__":
    main()
