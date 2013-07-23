# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path
import re
import Image
import shutil

from ..image import ImageRef
from ..util import *
from .. import config

class PDFToPPM(object):
    def __init__(self, input_file, dpi):
        object.__init__(self)
        self.pdf_fn = input_file
        self.work_dir = os.path.join(config.get_work_dir(), 'pdftoppm')
        makedirs(self.work_dir)
        self.output_prefix = os.path.join(self.work_dir, 'out')
        self.dpi = dpi
    def to_image(self, page_no):
        spage_no = '%d' % (page_no,)
        sdpi = '%d' % (self.dpi,)
        check_call(['pdftoppm', '-r', sdpi, '-f', spage_no,
                    '-l', spage_no, '-png', self.pdf_fn,
                    self.output_prefix])
        fns = os.listdir(self.work_dir)
        fns = [os.path.join(self.work_dir, fn) for fn in fns]
        re_img_fn = re.compile('%s-0*%d.png' % (self.output_prefix, page_no))
        img_fns = [fn for fn in fns if re_img_fn.match(fn)]
        assert(len(img_fns) == 1)
        return ImageRef(file_name = img_fns[0])

class PDFImage(object):
    def __init__(self, input_file):
        object.__init__(self)
        self.pdf_fn = input_file
        self.work_dir = os.path.join(config.get_work_dir(), 'pdfimage')
        makedirs(self.work_dir)
        self.output_prefix = os.path.join(self.work_dir, 'out')
        self.re_out_fn = re.compile('out-0[0-9]*\\.(ppm|pbm)')
        self.pdf_to_ppm = PDFToPPM(input_file, 100)
    def to_image(self, page_no):
        spage_no = '%d' % (page_no,)
        check_call(['pdfimages', '-f', spage_no, '-l', spage_no,
                    self.pdf_fn, self.output_prefix])
        fns = os.listdir(self.work_dir)
        out_fns = [fn for fn in fns if self.re_out_fn.match(fn)]
        out_fns = [os.path.join(self.work_dir, fn) for fn in out_fns]
        nout_fns = len(out_fns)
        if nout_fns != 1:
            print 'PDFImage.get_page: %d images generated for page %d' % \
                (nout_fns, page_no)
            for out_fn in out_fns:
                pass #os.unlink(out_fn)
            return self.pdf_to_ppm.to_image(page_no)
        out_fn = out_fns[0]
        r, ext = os.path.splitext(out_fn)
        img_fn = 'page-%06d%s' % (page_no, ext)
        img_fn = os.path.join(self.work_dir, img_fn)
        shutil.move(out_fn, img_fn)
        return ImageRef(file_name = img_fn)

def create_pdf_to_image(conf):
    if conf.input_type == 'image':
        return PDFImage(conf)
    else:
        return PDFToPPM(conf)
