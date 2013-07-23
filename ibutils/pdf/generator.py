# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import Image
from reportlab.pdfgen import canvas

class PDFGenerator(object):
    def __init__(self):
        object.__init__(self)
    def generate(self, out_file, bk):
        def map_page_num(pm, pn):
            if pm is None:
                return pn
            elif pm.has_key(pn):
                return pm[pn] - 1
            else:
                return -1
        def gen_page_to_bm_map(bms, pm):
            p2bm = {}
            for bm in bms:
                opn = map_page_num(pm, bm.page)
                if opn != -1:
                    if not p2bm.has_key(opn):
                        p2bm[opn] = []
                    p2bm[opn].append(bm.title)
            return p2bm
        c = canvas.Canvas(out_file)
        c.setTitle(bk.title)
        c.setAuthor(bk.author)
        p2bm = gen_page_to_bm_map(bk.bookmarks, bk.page_map)
        for opn, fn in enumerate(bk.img_files):
            img = Image.open(fn)
            c.setPageSize(img.size)
            c.drawImage(fn, 0, 0)
            if p2bm.has_key(opn):
                for n, t in enumerate(p2bm[opn]):
                    key = '%d-%d' % (opn, n)
                    c.bookmarkPage(key)
                    c.addOutlineEntry(t, key, 0, 0)
            c.showPage()
        c.save()
