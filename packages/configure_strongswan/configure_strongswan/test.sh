#! /bin/bash -e

WORD_PROG=./gen_word.sh
WORDS=`$WORD_PROG 50`

WORD=""
WORD_INDEX=0
function next_word() {
	shift $WORD_INDEX
	WORD=$1
	WORD_INDEX=$[WORD_INDEX + 1]
}

CLIENT_SUBJ="/C=US/ST=MD/L=Columbia/O="
next_word $WORDS
ORG=$WORD
next_word $WORDS
CLIENT_SUBJ=$WORD
next_word $WORDS
USER=$WORD
next_word $WORDS
DOMAIN=$WORD
next_word $WORDS

DOMAIN=$DOMAIN.com
EMAIL=$USER@$DOMAIN
CLIENT_SUBJ=$SUBJ"/CN=$DOMAIN/emailAddress=$EMAIL"

CONN_NAME=$WORD
next_word $WORDS

declare -a PASS
for i in {1..4};
do
	PASS[$i]=$WORD
	next_word $WORDS
done

CLIENT_PASSWD="${PASS[1]}-${PASS[2]}-${PASS[3]}-${PASS[4]}"

echo $CLIENT_SUBJ
echo $CONN_NAME
echo $CLIENT_PASSWD
