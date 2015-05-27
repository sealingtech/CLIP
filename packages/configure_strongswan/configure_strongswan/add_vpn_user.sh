#! /bin/bash -e

#TODO source common variables from a script

. /usr/bin/vpn_funcs.sh

gen_cert_subj CLIENT_SUBJ
gen_random_word CONN_NAME
gen_passwd CLIENT_PASSWD

WORKDIR=/tmp/add_vpn_user
CLIENT_KEY=$WORKDIR/$CONN_NAME.key
CLIENT_PEM=$WORKDIR/$CONN_NAME.pem
CLIENT_P12=$WORKDIR/$CONN_NAME.p12
CA_PEM=/etc/strongswan/ipsec.d/cacerts/ca.pem
CA_KEY=/etc/strongswan/ipsec.d/private/rootCA.key
CA_P12=/etc/strongswan/ipsec.d/cacerts/ca.crt
CERTDIR=/etc/strongswan/ipsec.d/certs/
PRIVATEDIR=/etc/strongswan/ipsec.d/private
CA_PASSWD_FILE=$PRIVATEDIR/ca_pass.txt
CA_PASSWD=`cat $CA_PASSWD_FILE`
DAYS=1024
REQUEST=$WORKDIR/request.csr

gen_key() {
        openssl genrsa -passout pass:$2 -out $1 4096
}

# args:
# $1 - key
# $2 - key password
# $3 - subject
# $4 - output file
ca_sign() {
        openssl req -new -key $1 -out $REQUEST -subj "$3" -passin pass:$2
        openssl x509 -req -in $REQUEST -CA $CA_PEM -CAkey $CA_KEY -CAcreateserial -out $4 -days $DAYS -passin pass:$CA_PASSWD
}

# arg1 is 1 for IKEV1 2 for IKEv2
if [ $1"x" != "1x" -a $1"x" != "2x" ]
then
	echo "invalid IKE parameter"
	exit -1	
fi


mkdir -p $WORKDIR
gen_key $CLIENT_KEY $CLIENT_PASSWD
ca_sign $CLIENT_KEY $CLIENT_PASSWD "$CLIENT_SUBJ" $CLIENT_PEM
openssl pkcs12 -export -out $CLIENT_P12 -inkey $CLIENT_KEY -in $CLIENT_PEM -passin pass:$CLIENT_PASSWD -passout pass:$CLIENT_PASSWD

XAUTH_INFO=""
XAUTH_USER=""
XAUTH_PASSWD=""

if [ $1"x" == "1x" ]
then
	CONN="conn $CONN_NAME\n\
        ike=aes256-sha1-modp1024!\n\
        esp=aes256-sha1!\n\
        keyexchange=ikev1\n\
        rightcert=$CONN_NAME.pem\n\
        rightauth2=xauth\n"

	gen_random_word XAUTH_USER
	gen_passwd XAUTH_PASSWD

	XAUTH_INFO="$XAUTH_USER : XAUTH $XAUTH_PASSWD"
else
	CONN="conn $CONN_NAME\n\
        ike=aes256-sha256-ecp384!\n\
        esp=aes256-aes128-sha384-sha256-ecp384-ecp256!\n\
        keyexchange=ikev2\n\
        rightcert=$CONN_NAME.pem\n"
fi

echo -e "$CONN" >> /etc/strongswan/ipsec.conf

if [ "$XAUTH_INFO""x" != "x" ]
then
	echo -e "$XAUTH_INFO" >> /etc/strongswan/ipsec.secrets
fi

OUTDIR=/home/sftp/android_certs/
CLIENT_PASSWD_FILE=$OUTDIR/client_pass.txt
XAUTH_INFO_FILE=$OUTDIR/xauth_info.txt

rm -rf $OUTDIR
mkdir -p $OUTDIR
cp $CLIENT_P12 $OUTDIR
cp $CA_P12 $OUTDIR
cp $CLIENT_PEM $CERTDIR
echo $CLIENT_PASSWD > $CLIENT_PASSWD_FILE
if [ $1"x" == "1x" ]
then
	echo $XAUTH_USER > $XAUTH_INFO_FILE
	echo $XAUTH_PASSWD >> $XAUTH_INFO_FILE
fi
rm -rf $WORKDIR
chown -R sftp:sftp $OUTDIR

#restart strongswan
service strongswan restart
