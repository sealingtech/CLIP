#!/usr/libexec/platform-python

import sys

def main():
	if (len(sys.argv) != 4):
		sys.stderr.write("usage: " + sys.argv[0] + " <name> <version> <arch>\n")
		sys.exit(-1)

	l = len(sys.argv[1] + " " + sys.argv[2] + " " + sys.argv[3])
	if l > 32:
		sys.stderr.write("length of volume ID is too long, shorten name by " + str(l - 32) + " characters\n")
		sys.exit(-1)

	print("Volume ID is valid")
	return 0

if __name__ == "__main__":
	main()
