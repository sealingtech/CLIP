#!/usr/libexec/platform-python
'''
Copyright (c) 2017 Quark Security, Inc. All rights reserved.
Author: Marshall Miller <marshall@quarksecurity.com>
'''

import sys
import os
import tempfile
import shutil
import argparse

from pykickstart.parser import *
from pykickstart.version import makeVersion
import dnf
import dnf.conf

sys.exit(0)

class KickstartPackageResolver(object):
    def __init__(self, ks_path, blacklist=None):
        self.ks_path = ks_path
        if blacklist is None:
            self.blacklist = []
        else:
            self.blacklist = blacklist

        # create a kickstart parser from the latest version
        self.ksparser = KickstartParser(makeVersion())
        self.yb = dnf.Base()

        self._repo_problems = False

    def parse(self):
        self.ksparser.readKickstart(self.ks_path)
        selected_package_names = list(self.ksparser.handler.packages.packageList)
        selected_group_names = list(self.ksparser.handler.packages.groupList)
        excluded_package_names = list(self.ksparser.handler.packages.excludedList)

        self.setup_yum()
        self.exclude_packages(excluded_package_names + self.blacklist)

        found, missing = self._find_packages(selected_package_names)
        if missing:
            raise Exception("failed to find %s" % (' '.join(missing),))

        for p in found:
            self.yb.install(p)
        for group in selected_group_names:
            tx_members = self.yb.group_install(group.name, "comps")

        result,msgs = self.yb.resolve()
        self._repo_problems = result != 2
        if self._repo_problems:
            sys.stderr.write("\n".join(msgs) + "\n")

    def cleanup(self):
        shutil.rmtree(self.tmpdir)

    @property
    def selected_packages(self):
        return [m.po for m in self.yb.tsInfo]

    def setup_yum(self):
        self.tmpdir = tempfile.mkdtemp(suffix=".ksparser")
        yum_conf = os.path.join(self.tmpdir, "fakyum.conf")
        yum_cache = os.path.join(self.tmpdir, "yumcache")

        # populate temporary yum tree
        with open(yum_conf, "a") as conf:
            conf.write("[main]\n")
            conf.write("installroot=%s\n" % (self.tmpdir,))
            conf.write("cachedir=%s\n" % (yum_cache,))
            conf.write("reposdir=%s/etc/yum/repos.d" % (self.tmpdir,))

        os.mkdir(yum_cache)
        os.mkdir(os.path.join(self.tmpdir, "etc"))
        os.mkdir(os.path.join(self.tmpdir, "etc/yum"))
        os.mkdir(os.path.join(self.tmpdir, "etc/yum/repos.d"))
        os.mkdir(os.path.join(self.tmpdir, "etc/yum.repos.d"))
        os.mkdir(os.path.join(self.tmpdir, "var"))
        os.mkdir(os.path.join(self.tmpdir, "var/lib"))
        os.mkdir(os.path.join(self.tmpdir, "var/lib/rpm"))

        # add and enable yum repos defined in the kickstart
        with open("%s/etc/yum/repos.d/repo.repo" % (self.tmpdir,), "w") as conf:
            for repodata in self.ksparser.handler.repo.repoList:
                conf.write("[%s]\n" % (repodata.name,))
                conf.write("name=%s\n" % (repodata.name,))
                conf.write("baseurl=%s\n" % (repodata.baseurl,))
                conf.write("enabled=1\n")

        self.yb.conf.read(yum_conf)
        self.yb.fill_sack(load_system_repo=False)
        self.yb.read_comps()

    def _find_packages(self, pkg_names, newest_only=True):
        found = []
        missing = []
        query = self.yb.sack.query().filterm(name=pkg_names)

        # some package patterns did not match, so look one at a time
        for pkg in query:
            print("found pkg %s" % (pkg,))
        return (found, missing)

    def exclude_packages(self, package_names):
        excluded_packages,_ = self._find_packages(package_names, newest_only=False)
        for p in excluded_packages:
            p.exclude()

    def what_requires(self, dep_name):
        # not sure how to find this yet.  maybe look through goal or selectors or solutions
        #for txm in self.yb.tsInfo:
        #    if txm.name == dep_name:
        #        required_by = [p[0].name for p in txm.relatedto]
        #        groups = ["@%s" % (g,) for g in txm.groups]
        #        result = required_by + groups or ["kickstart"]
        #        return result
        return ["unknown"]

    @property
    def problems(self):
        return self._repo_problems

    @property
    def packages_nvra(self):
        nvra = [p.nvra for p in self.selected_packages]
        nvra.sort()
        return nvra

    def write_packages_info(self, out=sys.stdout):
        out.write("\n".join(self.packages_nvra) + "\n")

    @property
    def packages_meta(self):
        meta = [(p.nvra, self.package_hash(p)) for p in self.selected_packages]
        meta.sort()
        return meta

    def package_hash(self, po):
        # TODO: canonicalize package metadata and return a hash of that
        # rather than a hash of the package file
        return po.pkgId

    def write_packages_meta(self, out=sys.stdout):
        meta = self.packages_meta
        out.write("\n".join([','.join(m) for m in meta]) + "\n")

    def strip_pseudo_pkgs(self, package_names):
        return [p for p in package_names if not p.startswith("gpg-pubkey-")]

    def get_extra_packages(self, baseline_packages):
        '''
        return a list of packages that are selected in the kickstart but
        are not present in baseline_packages
        '''
        extra = list(set(self.packages_nvra) - set(self.strip_pseudo_pkgs(baseline_packages)))
        extra.sort()
        return extra

    def write_extra_packages(self, baseline_packages, out=sys.stdout):
        extra = self.get_extra_packages(baseline_packages)
        out.write("\n".join(extra) + "\n")

    def write_extra_packages_and_why(self, baseline_packages, out=sys.stdout):
        extra = self.get_extra_packages(baseline_packages)
        extra_packages = self.get_selected_package_objects_by_nvra(extra)
        for p in extra_packages:
            requires = self.what_requires(p.name)
            if requires is None:
                msg = "%s is not selected" % (p.nvra,)
            elif not requires:
                msg = "%s required by nothing" % (p.nvra,)
            else:
                msg = "%s required by %s" % (p.nvra, ' '.join(requires))
            out.write(msg + "\n")

    def get_selected_package_objects_by_nvra(self, packages_nvra):
        ''' return the list of selected package objects that match the list of nvra strings '''
        matching_packages = []
        for package in self.selected_packages:
            for nvra in packages_nvra:
                if package.nvra == nvra:
                    matching_packages.append(package)
        return matching_packages

    def get_missing_packages(self, baseline_packages):
        '''
        return a list of packages that are present in baseline_packages
        but are not selected in the kickstart
        '''
        missing = list(set(self.strip_pseudo_pkgs(baseline_packages)) - set(self.packages_nvra))
        missing.sort()
        return missing

    def write_missing_packages(self, baseline_packages, out=sys.stdout):
        missing = self.get_missing_packages(baseline_packages)
        out.write("\n".join(missing) + "\n")

def package_list_file(path):
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("path %s does not exist" % (path,))
    value = []
    for line in file(path):
        line = line.strip()
        if not line or line[0] == '#':
            continue
        value.append(line)
    return value


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--blacklist",
                        help="path to a file containing packages to exclude",
                        type=package_list_file)
    parser.add_argument("-o", "--output",
                        help="path to a file to output selected package info",
                        type=argparse.FileType("w"))
    parser.add_argument("--expected",
                        help="path to a file containing expected package results",
                        type=package_list_file)
    parser.add_argument("--missing",
                        help="path to a file to output packages missing when compared to expected",
                        type=argparse.FileType("w"))
    parser.add_argument("--extra",
                        help="path to a file to output extra packages when compared to expected",
                        type=argparse.FileType("w"))
    parser.add_argument("--why-extra",
                        help="also output info for why extra packages are present when used in conjunction with --extra",
                        action="store_true")
    parser.add_argument("--with-meta",
                        help="also output metadata for packages",
                        action="store_true")
    parser.add_argument("kickstart", help="path to the kickstart file")
    args = parser.parse_args(argv)

    if not args.expected and (args.missing or args.extra):
        parser.error("--missing and --extra require --expected")

    pkg_resolver = KickstartPackageResolver(args.kickstart, args.blacklist)
    pkg_resolver.parse()
    if pkg_resolver.problems:
        sys.stderr.write("error: something is wrong with the kickstart or yum repos\n")
        sys.exit(1)

    if args.output:
        args.output.write("# selected packages\n")
        if args.with_meta:
            pkg_resolver.write_packages_meta(args.output)
        else:
            pkg_resolver.write_packages_info(args.output)

    if args.missing:
        args.missing.write("# missing packages\n")
        pkg_resolver.write_missing_packages(args.expected)

    if args.extra:
        args.extra.write("# extra packages\n")
        if args.why_extra:
            pkg_resolver.write_extra_packages_and_why(args.expected)
        else:
            pkg_resolver.write_extra_packages(args.expected)

    pkg_resolver.cleanup()

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
