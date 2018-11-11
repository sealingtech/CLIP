#!/usr/bin/python
'''
Copyright (c) 2018 Quark Security, Inc. All rights reserved.
Author: Marshall Miller <marshall@quarksecurity.com>
'''

import sys
import os
import tempfile
import shutil
import argparse
import subprocess

# run a command and return the stdout and stderr from the process
def get_command_output(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    rc = proc.wait()
    if rc != 0:
        raise Exception("command '%s' failed with rc %s" % (" ".join(cmd), rc))
    return stdout, stderr

# run a command
def run_command(cmd, **kwargs):
    proc = subprocess.Popen(cmd, **kwargs)
    rc = proc.wait()
    if rc != 0:
        raise Exception("command '%s' failed with rc %s" % (" ".join(cmd), rc))

# find the location of an executable
def locate_executable(exe):
    try:
        loc, _ = get_command_output(["which", exe])
        loc = loc.strip()
        if not os.path.exists(loc):
            raise Exception("failed to locate %s" % (exe,))
    except Exception as e:
        raise Exception("failed to locate %s: %s" % (exe, str(e)))

    return loc

# locate dependencies
ISO_INFO = locate_executable("iso-info")
MKISOFS = locate_executable("mkisofs")
IMPLANTISOMD5 = locate_executable("implantisomd5")

# class to help with modifying an existing iso
class IsoRepacker(object):
    def __init__(self, orig_iso_path, new_iso_path, command=None):
        self.orig_iso_path = orig_iso_path
        self.new_iso_path = new_iso_path
        self.command = command

        self.workdir = None
        self.iso_mountpoint = None
        self.extracted_dir = None
        self.iso_mounted = False

    def repack(self):
        try:
            self._setup()
            self._unpack()
            self._run_update_command()
            self._pack()
        except Exception as e:
            self._cleanup()
            print("error: %s" % (str(e),))
            raise
        self._cleanup()

    def _get_orig_volname(self):
        iso_info, _ = get_command_output([ISO_INFO, "-i", self.orig_iso_path])
        for line in iso_info.split("\n"):
            if "Volume" in line:
                return line.split()[2]
        raise Exception("failed to find the original volume name")

    def _setup(self):
        self.workdir = tempfile.mkdtemp(suffix='', prefix="isorepack-")

        self.iso_mountpoint = os.path.join(self.workdir, "orig")
        self.extracted_dir = os.path.join(self.workdir, "new")

    def _cleanup(self):
        if self.iso_mounted and self.iso_mountpoint:
            run_command(["sudo", "umount", self.iso_mountpoint])
            self.iso_mounted = False

        if self.workdir and os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
            self.workdir = None

        self.iso_mountpoint = None
        self.extracted_dir = None

    def _unpack(self):
        os.makedirs(self.iso_mountpoint)
        run_command(["sudo", "mount", "-o", "loop", self.orig_iso_path, self.iso_mountpoint])
        self.iso_mounted = True
        shutil.copytree(self.iso_mountpoint, self.extracted_dir)

    def _run_update_command(self):
        if not self.command:
            print("modify contents of iso rooted at %s and exit the shell to continue" % (self.extracted_dir,))
            command = ["/bin/bash"]
            env = {"PS1":r"[isorepack: \u@\h \W]\$ "}
        else:
            env = None
            command = [self.command[0]]
            for arg in self.command[1:]:
                if arg == "%ISO_ROOT":
                    command.append(self.extracted_dir)
                else:
                    command.append(arg)
        run_command(command, env=env)

    def _pack(self):
        run_command([
            MKISOFS,
            "-f", "-v", "-U", "-J", "-R", "-T",
            "-m", "repoview",
            "-m", "boot.iso",
            "-b", "isolinux/isolinux.bin",
            "-c", "isolinux/boot.cat",
            "-no-emul-boot",
            "-boot-load-size", "4",
            "-boot-info-table",
            "-eltorito-alt-boot",
            "-e", "images/efiboot.img",
            "-no-emul-boot",
            "-V", self._get_orig_volname(),
            "-o", self.new_iso_path,
            self.extracted_dir
        ])
        run_command([IMPLANTISOMD5, self.new_iso_path])

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("orig_iso", help="path to the original iso")
    parser.add_argument("new_iso", help="path to output the new iso to")
    parser.add_argument("command", nargs="*",
        help="""optional command to be executed after the original
              iso has been extracted and before the new iso is generated.  if
              no command is supplied then an interactive shell will run to
              allow manual modifications to the iso.  the output iso will
              be generated when the interactive shell exits.  an argument of
              %%ISO_ROOT will be replaced with the path to the extracted iso""")
    args = parser.parse_args(argv)

    if not os.path.exists(args.orig_iso):
        print("error: the path supplied for the original iso does not exist")
        return 1

    if os.path.exists(args.new_iso):
        print("error: the path supplied for the new iso already exists")
        return 1

    repacker = IsoRepacker(args.orig_iso, args.new_iso, args.command)
    repacker.repack()

    print("successfully created updated iso at %s" % (args.new_iso,))

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
