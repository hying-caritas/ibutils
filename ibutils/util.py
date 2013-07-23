# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import tempfile
import math
import re
import subprocess
import errno
import os
import sys

def temp_file_name(sfx = None, dir = None):
    fh, fn = tempfile.mkstemp(suffix = sfx, dir = dir)
    return fn

def near_zero(f):
    return f < 1e-6

def nround(f):
    return int(round(f))

def nceil(f):
    return int(math.ceil(f))

def nfloor(f):
    return int(math.floor(f))

def middle(list):
    sl = sorted(list)
    return sl[len(sl) / 2]

def str2bool(x):
    return bool(int(x))

def str2percent(x):
    return float(x) / 100.

class kv(dict):
    re_l = re.compile(r'^\s*([^#:\s][^:\s]+)\s*:\s*(\S.*)$')
    def __init__(self, f = None):
        dict.__init__(self)
        if f:
            self.load(f)
    def load(self, f):
        for l in f:
            r = kv.re_l.match(l)
            if r:
                self[r.group(1)] = r.group(2)
    def save(self, f):
        for k, v in self.iteritems():
            f.write('%s:\t%s\n' % (k, str(v)))
    def merge(self, akv):
        for k, v in akv.iteritems():
            self[k] = v
    def get(self, key, defult = None, conv = str):
        if self.has_key(key):
            return conv(self[key])
        else:
            return defult

class CommandNotFound(Exception):
    def __init__(self, cmd):
        Exception.__init__(self)
        self.cmd = cmd
    def __str__(self):
        return 'Command not found: %s' % (self.cmd,)

def call_wrapper(call, *popenargs, **kwargs):
    try:
        ret = 0
        ret = call(*popenargs, **kwargs)
    except OSError, e:
        if e.errno == errno.ENOENT:
            if kwargs.has_key('executable'):
                cmd = kwargs['executable']
            else:
                cmd = popenargs[0][0]
            raise CommandNotFound(cmd)
        else:
            raise e
    return ret

def check_call(*popenargs, **kwargs):
    return call_wrapper(subprocess.check_call, *popenargs, **kwargs)

def Popen(*popenargs, **kwargs):
    return call_wrapper(subprocess.Popen, *popenargs, **kwargs)

PIPE = subprocess.PIPE

def makedirs(dir):
    try:
        os.makedirs(dir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise e

def error_exit(msg, exit_code=-1):
    sys.stderr.write("Error: ")
    sys.stderr.write(msg)
    sys.exit(exit_code)

def error_exit_if(cond, msg, exit_code=-1):
    if cond:
        error_exit(msg, exit_code)
