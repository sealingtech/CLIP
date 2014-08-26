Here is a quick list of the things you need to do to get started.

Big Hint/Suggestion: if you use Quark Security's build VM
you can skip steps 1-4.  Why not make your life easier by
downloading it:
[Quark Security's CLIP build VM](https://quarksecurity.com/files/CLIP/)


1. Add your user to /etc/sudoers (required since mock and livecd creator use
chroots)

2. CHANGE THE DEFAULT PASSWORD IN YOUR KICKSTART (kickstarts/clip-minimal/clip-minimal.ks)!
CLIP intentionally ships with an unencrypted default password!  It is "neutronbass".  
DO NOT LEAVE THIS PASSWORD LINE INTACT!

3. Go back and re-read #2.

4. Run "./bootstrap.sh". 

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

6. [Help-LiveCDs.txt](Help-LiveCDs.txt)
   
   How to generate live CDs.

7. [Help-Released-Upstream-Packages.txt](Help-Released-Upstream-Packages.txt)

   How to add an upstream package and track it.

8. [Help-Releases.txt](Help-Releases.txt)

   Help in getting a CLIP release out.

9. [Help-SecState.txt](Help-SecState.txt)

   How to use SecState's remediation functionality.

10. [Help-Updating-Existing-External-Packages.txt](Help-Updating-Existing-External-Packages.txt)

   Hot to update the existing external packages that are used.

11. [Help-Upstream-Git-Repos.txt](Help-Upstream-Git-Repos.txt)

   How to track an upstream repo using a specific git hash.

12. [Help-Upstreams.txt](Help-Upstreams.txt)

   How to add various upstream packages.

13. [Help-Upstream-SVN-Repos.txt](Help-Upstream-SVN-Repos.txt)

   How to track an upstream repo using a specific SVN hash.

14. [Help-Use-Cases.txt](Help-Use-Cases.txt)

   How to best use CLIP for specific scenarios.
