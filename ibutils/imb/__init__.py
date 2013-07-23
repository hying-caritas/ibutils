# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path
import shutil
from xml.sax.saxutils import escape
from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, ContentHandler
import codecs

from ..util import *

class Page(object):
    def __init__(self, img_fn, num):
        object.__init__(self)
        self.img_fn = img_fn
        self.num = num

class TocEntry(object):
    def __init__(self, title=None, page_num=None):
        object.__init__(self)
        self.title = title
        self.page = page_num

class Book(object):
    def __init__(self, title=None, author=None):
        object.__init__(self)
        self.pages = []
        self.toc_entries = []
        self.title = title
        self.author = author
    def add_page(self, img_fn):
        pg = Page(img_fn, len(self.pages)+1)
        self.pages.append(pg)
        return pg
    def add_toc_entry(self, title, pg):
        entry = TocEntry(title, pg.num)
        self._add_toc_entry(entry)
    def _add_toc_entry(self, entry):
        self.toc_entries.append(entry)
    def save(self, out_fn, move_image = False):
        outf = codecs.open(out_fn, "wb", "utf-8")
        (s, ext) = os.path.splitext(out_fn)
        outd = s + '_imgs'
        outd_base = os.path.basename(outd)
        if os.path.isdir(outd):
            shutil.rmtree(outd)
        elif os.path.exists(outd):
            os.unlink(outd)
        os.mkdir(outd)

        for pg in self.pages:
            (s, ext) = os.path.splitext(pg.img_fn)
            nfn_base = '%05d%s' % (pg.num, ext)
            nfn = os.path.join(outd, nfn_base)
            if move_image:
                shutil.move(pg.img_fn, nfn)
            else:
                shutil.copyfile(pg.img_fn, nfn)
            pg.dimg_fn = os.path.join(outd_base, nfn_base)

        outf.write('<?xml version="1.0" encoding="utf-8"?>\n')
        outf.write('<imb>\n')
        if self.title:
            s = u'\t<book_title>%s</book_title>\n' % (escape(self.title),)
            outf.write(s)
        if self.author:
            s = '\t<author>%s</author>\n' % (escape(self.author),)
            outf.write(s)
        outf.write('\t<page_num>%d</page_num>\n' % (len(self.pages),))
        outf.write('\t<pages>\n')
        for pg in self.pages:
            outf.write('\t\t<page>%s</page>\n' % escape(pg.dimg_fn))
        outf.write('\t</pages>\n')
        outf.write('\t<toc>\n')
        for entry in self.toc_entries:
            outf.write('\t\t<entry>\n')
            s = u'\t\t\t<title>%s</title>\n' % (escape(entry.title),)
            outf.write(s)
            outf.write('\t\t\t<page>%d</page>\n' % (entry.page,))
            outf.write('\t\t</entry>\n')
        outf.write('\t</toc>\n')
        outf.write('</imb>\n')
        outf.close()
    def load(self, in_fn):
        f = file(in_fn)
        dir = os.path.dirname(in_fn)
        parser = make_parser()
        parser.setFeature(feature_namespaces, 0)
        dh = IMBHandler(self, dir)
        parser.setContentHandler(dh)
        parser.parse(f)

class IMBHandler(ContentHandler):
    def __init__(self, book, dir):
        ContentHandler.__init__(self)
        self.book = book
        self.dir = dir
        self.entry = None
    def startElement(self, name, attrs):
        if name == 'entry':
            self.entry = TocEntry()
        else:
            self.curr_elem = name
    def endElement(self, name):
        if name == 'entry' and self.entry.title and self.entry.page:
            self.book.toc_entries.append(self.entry)
            self.entry = None
        self.curr_elem = None
    def characters(self, ch):
        book = self.book
        if self.entry:
            if self.curr_elem == 'title':
                self.entry.title = ch
            elif self.curr_elem == 'page':
                self.entry.page = int(ch)
        elif self.curr_elem == 'book_title':
            book.title = ch
        elif self.curr_elem == 'author':
            book.author = ch
        elif self.curr_elem == 'page':
            book.add_page(os.path.join(self.dir, ch))
