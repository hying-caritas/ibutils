# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path

from .. import imb
from ..image import ImageRef
from ..util import *

class IMBToImage(object):
    def __init__(self, input_file):
        object.__init__(self)
        self.imgs_dir = input_file
        self.output_prefix = os.path.join(config.get_work_dir(), 'out')
        self.imbook = imb.Book()
        self.imbook.load(input_file)
    def to_image(self, page_no):
        iimg_fn = self.imbook.pages[page_no-1].img_fn
        oimg_fn = "%s-%d.pgm" % (self.output_prefix, page_no)
        check_call(['convert', iimg_fn, oimg_fn])
        return ImageRef(file_name = oimg_fn)
