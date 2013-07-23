# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from .. import imb

def map_page_num(page_map, pn):
    if page_map is None:
        return pn
    elif page_map.has_key(pn):
        return page_map[pn] - 1
    else:
        return -1

class IMBGenerator(object):
    def __init__(self):
        object.__init__(self)
    def generate(self, out_file, bk):
        imbk = imb.Book(title=bk.title, author=bk.author)
        pgs = []
        for fn in bk.img_files:
            pg = imbk.add_page(fn)
            pgs.append(pg)
        for bm in bk.bookmarks:
            opn = map_page_num(bk.page_map, bm.page)
            if opn != -1:
                imbk.add_toc_entry(bm.title, pgs[opn-1])
        imbk.save(out_file)
