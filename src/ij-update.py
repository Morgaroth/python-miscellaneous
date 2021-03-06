#!/usr/bin/env python3
# coding=utf-8
import os
import sys
from subprocess import Popen
from os import remove, symlink
from os.path import join, exists
import errno
from shutil import move

"""
    Script for updating IntelliJ EAP version, using downloaded by user tarball
"""


INTELLIJ = join('/', 'apps', 'IntelliJ')

if len(sys.argv) < 2:
    print("missing arguments, provide file of IntelliJ to update")
    sys.exit(-1)

if len(sys.argv) > 2:
    print("too much arguments, provide only file of IntelliJ to update")
    sys.exit(-1)


def strip_postfix(src, postfix):
    if src.endswith(postfix):
        return src[:-(len(postfix))]
    else:
        return src


source_file = sys.argv[1]
source_link = join(os.getcwd(), source_file)
Popen(['tar', '-xzf', source_link], cwd='/tmp').wait()
candidates = [f for f in os.listdir('/tmp') if f.startswith("idea-")]
if len(candidates) > 1:
    print("there is more than one candidate to be extracted directory", candidates)

if len(candidates) == 0:
    print("there isn't candidates to be extracted directory", candidates)

name = candidates[0]
target = join(INTELLIJ, name)

if exists(target):
    print("Version %s already exists in /apps/IntelliJ")
    sys.exit(-2)

move(join('/tmp', name), target)
current_link = join(INTELLIJ, 'current')
try:
    remove(current_link)
except OSError as e:
    if e.errno != errno.ENOENT:
        raise
symlink(target, current_link)
