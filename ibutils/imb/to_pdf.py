# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import sys
import Image

from ..pdf import generator
from .. import imb

class Config(object):
    def __init__(self):
        object.__init__(self)

def imb2pdf(in_fn, out_fn):
    imbook = imb.Book()
    imbook.load(in_fn)
    if len(imbook.pages) == 0:
        return
    img_fns = [pg.img_fn for pg in imbook.pages]
    img = Image.open(imbook.pages[0].img_fn)
    config = Config()
    config.title = imbook.title
    config.author = imbook.author
    config.bookmarks = imbook.toc_entries
    config.out_size = img.size
    config.rotate = 0
    config.out_file_name = out_fn

    pg = pdf.generator.PDFGenerator(config)
    pg.generate(img_fns)

def usage():
    print 'Usage: %s <input file>.imb <output file>.pdf' % (sys.argv[0],)
    sys.exit(-1)

def main():
    if len(sys.argv) != 3:
        usage()
    imb2pdf(sys.argv[1], sys.argv[2])
