#!/usr/bin/env python3
import os
import sys
import subprocess
import itertools

__author__ = 'mateusz'


def execute(command, verbose=False):
    def prepare_command():
        cmd = command
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        if not isinstance(cmd, list):
            raise Exception("Neither string nor list passed to execute command")
        return cmd

    cmd = prepare_command()
    if verbose:
        print("executing command:\n\t%s" % cmd)
    process = subprocess.Popen(cmd, env=os.environ.copy(), stdout=subprocess.PIPE)
    out, err = process.communicate()
    ret_code = process.returncode
    return out, err, ret_code


prefix = sys.argv[1]
prefix_name = prefix
if prefix_name.endswith('_'):
    prefix_name = prefix_name[:-1]

cwd = os.getcwd()
files = [f for f in os.listdir(cwd) if f.startswith(prefix)]
files_input = list(itertools.chain.from_iterable([['-f', f] for f in files]))

merge_options = ['-x', 'track,merge,title="%s"' % prefix_name]

execute(['gpsbabel', '-t', '-i', 'gpx'] + files_input + merge_options + ['-o', 'gpx', '-F', '%s.gpx' % prefix_name])