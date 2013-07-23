# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path
from ..util import *
from .. import imb

class ImbInfo(object):
    def __init__(self, doc_title, author, pgs):
        object.__init__(self)
        self.doc_title = doc_title
        self.author = author
        self.pages = pgs

class ImbInfoParser(object):
    def __init__(self, imb_file):
        object.__init__(self)
        self.imb_fn = imb_file
    def parse(self):
        book = imb.Book()
        book.load(self.imb_fn)
        info = ImbInfo(book.title, book.author, len(book.pages))
        return (info, book.toc_entries)

def print_bookmarks(bms):
    for bm in bms:
        print bm.title.encode('utf-8'), bm.page

if __name__ == '__main__':
    import sys
    info = get_info(sys.argv[1])
    print 'title:', info.doc_title.encode('utf-8')
    print 'author:', info.author.encode('utf-8')
    print 'pages:', info.pages
    print_bookmarks(info.bookmarks)
