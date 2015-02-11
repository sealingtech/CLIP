THIS IS AN CLIP VARIANT IN AN ALPHA STATE!
NO NOT USE IN PRODUCTION!

Notes:
1. To do this right, after deployment, login as toor, sudo.
2. Populate toor's ~/.ssh/authorized_keys file
w/ admin key material.
3. Populate sftp dropbox user's ~/.ssh/authorized_keys
file.
4. Change the ownersip of the sftp user's .ssh/authorized_keys
to prevent the user from uploading new keys:
chown root .ssh/authorized_keys

