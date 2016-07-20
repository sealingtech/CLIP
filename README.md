Here is a quick list of the things you need to do to get started.

Big Hint/Suggestion: if you use Quark Security's build VM
you can skip steps 1-4.  Why not make your life easier by
downloading it:
[Quark Security's CLIP build VM](http://test.quarksecurity.com/opensource.shtml)


1. Add your user to /etc/sudoers (required since mock and livecd creator use
chroots).

Note that this line is required to generate media.

2. CHANGE THE DEFAULT PASSWORD IN YOUR KICKSTART (kickstarts/clip-minimal/clip-minimal.ks)!
CLIP intentionally ships with an unencrypted default password!  It is "neutronbass".  
DO NOT LEAVE THIS PASSWORD LINE INTACT!

3. Go back and re-read #2.

4. Run "./bootstrap.sh" or "./bootstrap.sh -c <config file>". See [Help-bootstrap-config.txt]
for details.

5. After you have run bootstrap once you do not have to run it again. 
Roll an ISO by running "$ make clip-minimal-inst-iso". This will generate
an installable ISO.  Alternatively, run "$ make clip-minimal-live-iso" 
to generate a live media ISO.

Note: for a complete list of targets available please run "$ make help".

After you have successfully rolled an installation ISO it is time to move on
to customizing the image.  Each topic related to customizing the image is
discussed in Help-*.txt files in the root of the CLIP repo.

For general questions please reference [Help-FAQ.txt](Help-FAQ.txt).
For more detailed instructions, you may reference the following:

1. [Help-Adding-Existing-Binary-Packages-to-Image.txt](Help-Adding-Existing-Binary-Packages-to-Image.txt)
   
   Assistance for adding binary packages to a rolled ISO.

2. [Help-Adding-Source-Packages.txt](Help-Adding-Source-Packages.txt)

   Assistance for adding source packages to the build system.

3. [Help-Build-System.txt](Help-Build-System.txt)
   
   Assistance in setting up the build system.

4. [Help-Generating-Live-Media.txt](Help-Generating-Live-Media.txt)

   How to generate live media.

5. [Help-Known-Issues.txt](Help-Known-Issues.txt)

   A list of currently known issues and how to get past them.

8. [Help-Releases.txt](Help-Releases.txt)

   Help in getting a CLIP release out.

9. [Help-Use-Cases.txt](Help-Use-Cases.txt)

   How to best use CLIP for specific scenarios.
