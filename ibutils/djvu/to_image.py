# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path

from ..image import ImageRef
from .. import config
from ..util import *

class DJVUToImage(object):
    def __init__(self, input_file):
        object.__init__(self)
        self.djvu_fn = input_file
        self.work_dir = os.path.join(config.get_work_dir(), 'djvutopgm')
        makedirs(self.work_dir)
        self.output_prefix = os.path.join(self.work_dir, 'out')
    def to_image(self, page_no):
        spage_no = '%d' % (page_no,)
        out_fn = self.output_prefix + '-' + spage_no
        check_call(['ddjvu', '-format=pgm', '-page=' + spage_no,
                    self.djvu_fn, out_fn])
        return ImageRef(file_name = out_fn)
