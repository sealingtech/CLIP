#! /usr/bin/python

import sys
import subprocess

def err(msg):
	sys.stderr.write(msg + "\n")
	exit(-1)

def main():
	try:
		print "configure strongswan"
		#expect the following:
		#line 1: ike version

		ike = 0
		ikeLine = sys.stdin.readline()
		if ikeLine == "":
			err("unexpected EOF")
		elif int(ikeLine.rstrip()) == 1:
			ike = "1"
		elif int(ikeLine.rstrip()) == 2:
			ike = "2"
		else:
			err("invalid ike line")

		rv = subprocess.call([ "/usr/bin/add_ss_user", ike])
		if rv != 0:
			err("something went wrong :(")
		else:
			print "successfully setup the user, login as the sftp user to get your credentials"

		exit(0)
	except Exception as e:
		err("unexpected exception: " + str(e))

if __name__ == "__main__":
	main()
