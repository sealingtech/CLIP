#! /bin/bash -e

WORD_PROG=/usr/bin/gen_word.sh
WORDS=`$WORD_PROG 50`
NEXT_WORD="\${WORD_ARRAY[WORD_INDEX]}; WORD_INDEX=\$[WORD_INDEX + 1]"

declare -a WORD_ARRAY
WORD_INDEX=0
for w in $WORDS;
do
	WORD_ARRAY[$WORD_INDEX]=$w
	WORD_INDEX=$[WORD_INDEX + 1]
done
WORD_INDEX=0

#$1 is the variable to update
function gen_passwd() {
	eval PASS=$NEXT_WORD
	for i in {0..2};
	do
		eval PASS=$PASS-$NEXT_WORD
	done
	eval $1=$PASS
}

#$1 is the variable to update
function gen_cert_subj() {
	SUBJ="/C=US/ST=MD/L=Columbia/O="
	eval ORG=$NEXT_WORD
	SUBJ="$SUBJ$ORG"
	eval USER=$NEXT_WORD
	eval DOMAIN=$NEXT_WORD
	DOMAIN=$DOMAIN.com
	EMAIL=$USER@$DOMAIN
	SUBJ=$CLIENT_SUBJ"/CN=$DOMAIN/emailAddress=$EMAIL"
	eval $1=$SUBJ
}

#$1 is the variable to update
#get the next random word
function gen_random_word() {
	eval $1=$NEXT_WORD
}

