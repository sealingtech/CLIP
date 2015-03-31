#! /bin/bash

function print_err()
{
	echo $1 1>&2
}

if [ $# -ne 3 ];
then
	print_err "usage: $0 <output> <workdir> <yum_conf>"
	exit -1
fi

OUTPUT=$1
WORKDIR=$2
STAGING_DIR=$WORKDIR/staging
YUM_CONF=$3

SOFTOKN_PKG=nss-softokn.x86_64
FREEBL_PKG=nss-softokn-freebl.x86_64

VER=`repoquery -c $YUM_CONF --qf=%{version} $SOFTOKN_PKG`
REL=`repoquery -c $YUM_CONF --qf=%{release} $SOFTOKN_PKG`
#strip the .el6_6 off
REL_NUM=`echo $REL | cut -d \. -f1`

RPM=nss-softokn-freebl-$VER-$REL.x86_64.rpm
CPIO=nss-softokn-freebl-$VER-$REL.x86_64.cpio
UPD_UPDATES=/usr/lib/anaconda-runtime/upd-updates

rm -rf $WORKDIR
mkdir -p $STAGING_DIR
cd $WORKDIR
yum clean all

##################################################################
# What's going on here?
# Starting with 3.14.3.22 nss-softokn requires nss-softokn-freebl,
# Unfortunately nss-softokn-freelbl 3.14.3.22 includes some new
# files that aren't in anaconda's hardcoded list of files to
# include in the installation media, so it rips them out.  So
# we create an anaconda update image that includes these required
# files
##################################################################
if [ "$VER" == "3.14.3" -a "$REL_NUM" -ge 22 ];
then
	yumdownloader -c $YUM_CONF $FREEBL_PKG
	if [ $? -ne 0 ];
	then
		print_err "failed to download $FREEBL_PKG"
		exit -1
	fi

	rpm2cpio $RPM > $CPIO
	cpio -idv < $CPIO

	##############################################################
	# How anaconda updates work:
	# whatever is in the anaconda update.img is dumped into
	# /tmp/updates
	# Before kicking off the installation /tmp/updates is
	# prepended to the following variables: PATH, LD_LIBRARY_PATH,
	# PYTHONPATH.  So whatever is in /tmp/updates takes precedence
	# over whatever's been rolled into the anaconda image.
	# We need these libs, so they need to be in the root of the
	# update.img
	##############################################################
	pushd lib64
	cp * $STAGING_DIR
	popd
fi

cd $STAGING_DIR
#this is really just so we don't end up with an empty update
echo "CLIP UPDPATES TO ANACONDA" > ./description.txt
find . -type f | xargs $UPD_UPDATES $OUTPUT

