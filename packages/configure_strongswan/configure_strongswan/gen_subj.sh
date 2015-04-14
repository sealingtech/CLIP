#! /bin/bash -e

GEN_WORD=/usr/bin/gen_word.sh
SUBJ="/C=US/ST=MD/L=Columbia/O="
ORG=`$GEN_WORD`
SUBJ="$SUBJ$ORG"
USER=`$GEN_WORD`
DOMAIN=`$GEN_WORD`
DOMAIN=$DOMAIN.com
EMAIL=$USER@$DOMAIN
SUBJ=$SUBJ"/CN=$DOMAIN/emailAddress=$EMAIL"

echo $SUBJ
