# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import tempfile
import shutil

from util import *

debug = False

work_dir = None
tmp_dir = None

def create_work_dir():
    global work_dir
    work_dir = tempfile.mkdtemp('ibutils')
    makedirs(work_dir)

def create_tmp_dir():
    global tmp_dir
    if work_dir is None:
        create_work_dir()
    tmp_dir = os.path.join(work_dir, 'tmp')
    makedirs(tmp_dir)

def get_work_dir():
    if work_dir is None:
        create_work_dir()
    return work_dir

def get_tmp_dir():
    if tmp_dir is None:
        create_tmp_dir()
    return tmp_dir

def clean_work_dir():
    shutil.rmtree(work_dir)
