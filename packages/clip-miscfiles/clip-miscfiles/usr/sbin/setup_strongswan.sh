#! /bin/bash

WORKDIR="/tmp/strongswan"
CA_KEY="$WORKDIR/rootCA.key"
CA_PEM="$WORKDIR/ca.pem"
CA_P12="$WORKDIR/ca.crt"
SERV_KEY="$WORKDIR/server.key"
SERV_PEM="$WORKDIR/server.pem"
CLIENT_KEY="$WORKDIR/client.key"
CLIENT_PEM="$WORKDIR/client.pem"
CLIENT_P12="$WORKDIR/client.p12"
IPSEC_CONF="$WORKDIR/ipsec.conf"
IPSEC_SECRETS="$WORKDIR/ipsec.secrets"
IPSEC_CONF_TMPL="$WORKDIR/ipsec.conf.tmpl"
IPSEC_SECRETS_TMPL="$WORKDIR/ipsec.secrets.tmpl"
ANDROID_CERTS="/tmp/android_certs"

mkdir -p $WORKDIR
cd $WORKDIR

cp /usr/share/strongswan/templates/config/ipsec.conf.tmpl $WORKDIR/
cp /usr/share/strongswan/templates/config/ipsec.secrets.tmpl $WORKDIR/

STRONGSWANDIR=/etc/strongswan
IPSECDIR=$STRONGSWANDIR/ipsec.d
CERTDIR=$IPSECDIR/certs
PRIVATEDIR=$IPSECDIR/private
CACERTDIR=$IPSECDIR/cacerts

DAYS=1024

install_files() {
	cp $CA_PEM $CACERTDIR
	cp $SERV_PEM $CERTDIR
	cp $CLIENT_PEM $CERTDIR
	cp $SERV_KEY $PRIVATEDIR
	cp $IPSEC_CONF $STRONGSWANDIR
	cp $IPSEC_SECRETS $STRONGSWANDIR
	mkdir -p $ANDROID_CERTS
	cp $CLIENT_P12 $ANDROID_CERTS
	cp $CA_P12 $ANDROID_CERTS
}

# args $1 - filename, $2 password
gen_key() {
	openssl genrsa -passout pass:$2 -out $1 2048
}

# args $1 - filename, $2 keyfile, $3 subject
self_sign() {
	openssl req -x509 -new -nodes -key $2 -days $DAYS -out $1 -subj $3
	openssl x509 -inform PEM -outform DER -in $1 -out $CA_P12
}

# args:
# $1 - key
# $2 - key password
# $3 - subject
# $4 - output file
ca_sign() {
	openssl req -new -key $1 -out request.csr -subj "$3" -passin pass:$2
	openssl x509 -req -in request.csr -CA $CA_PEM -CAkey $CA_KEY -CAcreateserial -out $4 -days $DAYS -passin pass:$2
}

# args
# $1 server key pass
# $2 xauth user
# $3 xauth pass
update_ipsec_secrets() {
	sed "s/{SERVERPASS}/$1/" $IPSEC_SECRETS_TMPL > $IPSEC_SECRETS
  	sed -i "s/{XAUTHUSER}/$2/" $IPSEC_SECRETS
	sed -i "s/{XAUTHPASS}/$3/" $IPSEC_SECRETS
}

# args
# $1 server IP
# $2 vpn subnet
# $3 tun IP address assigned to client
update_ipsec_conf() {
        sed "s/{LEFTIP}/$1/" $IPSEC_CONF_TMPL > $IPSEC_CONF
	sed -i "s/{LEFTSUBNET}/$2/" $IPSEC_CONF
	sed -i "s/{RIGHTIP}/$3/" $IPSEC_CONF
}

echo "Enter CA cert subject:"
read CA_SUB
echo "Enter CA passwd:"
read -s CA_PASS
gen_key $CA_KEY $CA_PASS
self_sign $CA_PEM $CA_KEY $CA_SUB

echo "Enter server cert subject:"
read SERV_SUB
echo "server sub: $SERV_SUB"
echo "Enter server passwd:"
read -s SERV_PASS
gen_key $SERV_KEY $SERV_PASS
ca_sign $SERV_KEY $SERV_PASS "$SERV_SUB" $SERV_PEM

echo "Enter client cert subject:"
read CLIENT_SUB
echo "Enter client passwd:"
read -s CLIENT_PASS
gen_key $CLIENT_KEY $CLIENT_PASS
ca_sign $CLIENT_KEY $CLIENT_PASS "$CLIENT_SUB" $CLIENT_PEM
#export a pkcs12 file for using on the client
openssl pkcs12 -export -out $CLIENT_P12 -inkey $CLIENT_KEY -in $CLIENT_PEM -passin pass:$CLIENT_PASS -passout pass:$CLIENT_PASS

echo "Enter Server IP address:"
read SERVER_IP

echo "Enter Left Subnet:"
read LEFT_SUBNET

echo "Enter tun IP address:"
read RIGHT_IP

echo "Enter XAuth user name:"
read XAUTH_USER

echo "Enter XAuth passphrase:"
read -s XAUTH_PASS

update_ipsec_secrets $SERV_PASS $XAUTH_USER $XAUTH_PASS
update_ipsec_conf $SERVER_IP "$LEFT_SUBNET" $RIGHT_IP

install_files

echo -e "All setup!\nInstall $ANDROID_CERTS/ca.crt and $ANDROID_CERTS/client.p12 on your device to connect!"
echo -e "Strongswan must be restarted.  Run\n\nrun_init /etc/init.d/strongswan restart"

rm -rf $WORKDIR
