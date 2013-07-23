# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os.path

import config
import image
from util import *

class Line(object):
    def __init__(self, pg, lbegin, lend):
        self.page = pg
        self.lbegin = lbegin
        self.lend = lend
    def height(self):
        return self.lend - self.lbegin
    def bbox(self):
        left, top, right, bottom = self.page.bbox()
        return [left, self.lbegin, right, self.lend]
    def move_to(self, nlbegin):
        height = self.height()
        self.lbegin = nlbegin
        self.lend = nlbegin + height

class Col(object):
    def __init__(self, pg, cbegin, cend):
        self.page = pg
        self.cbegin = cbegin
        self.cend = cend
    def width(self):
        return self.cend - self.cbegin
    def bbox(self):
        left, top, right, bottom = self.page.bbox()
        return [self.cbegin, top, self.cend, bottom]
    def move_to(self, ncbegin):
        width = self.width()
        self.cbegin = ncbegin
        self.cend = ncbegin + width

class Page(object):
    def __init__(self, book, page_no, img_ref):
        object.__init__(self)
        self.book = book
        self.page_no = page_no
        self.render_img_ref = img_ref
    def has(self, attr):
        return getattr(self, attr, None) is not None
    def width(self):
        return 1.0
    def height(self):
        if self.has('render_img_ref'):
            img = self.render_img_ref.get_image()
        elif self.has('parse_img_ref'):
            img = self.parse_img_ref.get_image()
        iw, ih = img.size
        return float(ih) / iw
    def norm2ppxl(self, *norms):
        img = self.parse_img_ref.get_image()
        return tuple([nround(norm * img.size[0]) for norm in norms])
    def ppxl2norm(self, *ppxls):
        img = self.parse_img_ref.get_image()
        return tuple([float(ppxl) / img.size[0] for ppxl in ppxls])
    def norm2rpxl(self, *norms):
        img = self.render_img_ref.get_image()
        return tuple([nround(norm * img.size[0]) for norm in norms])
    def rpxl2norm(self, *rpxls):
        img = self.render_img_ref.get_image()
        return tuple([float(rpxl) / img.size[0] for rpxl in rpxls])
    def bbox(self):
        left = 0
        top = 0
        right = self.width()
        bottom = self.height()
        if self.has('_bbox'):
            left, top, right, bottom = self._bbox
        if self.has('lines'):
            top = self.lines[0].lbegin
            bottom = self.lines[-1].lend
        if self.has('cols'):
            left = self.cols[0].cbegin
            right = self.cols[-1].cend
        return [left, top, right, bottom]
    def set_bbox(self, bbox):
        self._bbox = bbox
    def rcrop(self, bbox):
        rpbbox = apply(self.norm2rpxl, bbox)
        img = self.render_img_ref.get_image()
        return img.crop(rpbbox)
    def rpaste(self, img, box):
        rpbox = apply(self.norm2rpxl, box)
        rimg = self.render_img_ref.get_image()
        rimg.paste(img, rpbox)
    def rclear(self, bbox):
        rpbbox = apply(self.norm2rpxl, bbox)
        img = self.render_img_ref.get_image()
        if img.mode != 'L':
            return
        img.paste(255, rpbbox)
    def start_lines(self):
        self.lines = []
    def append_line(self, lbegin, lend):
        ln = Line(self, lbegin, lend)
        self.lines.append(ln)
    def set_lines_bal(self):
        lines = self.lines
        lines[0].bl =  lines[0].lbegin
        lines[-1].al = self.height() - lines[-1].lend
        nlines = len(lines)
        for i in range(1, nlines):
            intvl = lines[i].lbegin - lines[i-1].lend
            lines[i-1].al = intvl
            lines[i].bl = intvl
    def end_lines(self):
        if len(self.lines) == 0:
            left, top, right, bottom = self.bbox
            self.append_line(top, bottom)
        self.set_lines_bal()
    def start_cols(self):
        self.cols = []
    def append_col(self, cbegin, cend):
        col = Col(self, cbegin, cend)
        self.cols.append(col)
    def set_cols_bac(self):
        cols = self.cols
        cols[0].bc = cols[0].cbegin
        cols[-1].ac = self.width() - cols[-1].cend
        ncols = len(cols)
        for i in range(1, ncols):
            intvl = cols[i].cbegin - cols[i-1].cend
            cols[i-1].ac = intvl
            cols[i].bc = intvl
    def end_cols(self):
        if len(self.cols) == 0:
            left, top, right, bottom = self.bbox
            self.append_col(left, right)
        self.set_cols_bac()

class PageConverter(object):
    def __init__(self):
        object.__init__(self)
    def end(self, pgs, bk):
        npgs = []
        for pg in pgs:
            pg = self.__call__(pg)
            if pg is not None:
                npgs.append(pg)
        return npgs

class PageParseConverter(PageConverter):
    def __init__(self, img_converter):
        PageConverter.__init__(self)
        self.img_converter = img_converter
    def __call__(self, pg):
        pg.parse_img_ref = self.img_converter(pg.parse_img_ref)
        return pg

class PageRenderConverter(PageConverter):
    def __init__(self, img_converter):
        PageConverter.__init__(self)
        self.img_converter = img_converter
    def __call__(self, pg):
        pg.render_img_ref = self.img_converter(pg.render_img_ref)
        return pg

class PageRenderToParse(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
    def __call__(self, pg):
        assert(not pg.has('parse_img_ref'))
        assert(pg.has('render_img_ref'))
        pg.parse_img_ref = pg.render_img_ref.dup()
        return pg

class PageBBox(PageConverter):
    def __init__(self, trim_left, trim_top, trim_right, trim_bottom):
        self.trim_left = trim_left
        self.trim_top = trim_top
        self.trim_right = trim_right
        self.trim_bottom = trim_bottom
    def __call__(self, pg):

        def not_empty(simg):
            h = simg.histogram()
            return sum(h[:-32]) > 0

        img = pg.parse_img_ref.get_image()
        pw, ph = img.size
        pleft = nround(self.trim_left * pw)
        ptop = nround(self.trim_top * ph)
        pright = pw - nround(self.trim_right * pw)
        pbottom = ph - nround(self.trim_bottom * ph)

        empty_page = True
        for x in range(pleft, pright):
            ic = img.crop((x, ptop, x+1, pbottom))
            if not_empty(ic):
                pleft = x
                empty_page = False
                break

        if empty_page:
            pg.set_bbox(pg.ppxl2norm(iw/2-5, ih/2-5, iw/2+5, ih/2+5))
            return pg

        for x in range(pright-1, pleft, -1):
            ic = img.crop((x, ptop, x+1, pbottom))
            if not_empty(ic):
                pright = x+1
                break

        for y in range(ptop, pbottom):
            ir = img.crop((pleft, y, pright, y+1))
            if not_empty(ir):
                ptop = y
                break

        for y in range(pbottom-1, ptop, -1):
            ir = img.crop((pleft, y, pright, y+1))
            if not_empty(ir):
                pbottom = y+1
                break

        pg.set_bbox(pg.ppxl2norm(pleft, ptop, pright, pbottom))
        return pg

class PageParser(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
    def __call__(self, pg):

        def is_empty(simg):
            h  = simg.histogram()
            return sum(h[:-32]) == 0

        img = pg.parse_img_ref.get_image()
        pleft, ptop, pright, pbottom = apply(pg.norm2ppxl, pg.bbox())

        in_line = False

        pg.start_lines()
        for y in range(ptop, pbottom):
            ir = img.crop((pleft, y, pright, y+1))
            emptyr = is_empty(ir)
            if in_line:
                if emptyr:
                    in_line =  False
                    plend = y
                    lbegin, lend = pg.ppxl2norm(plbegin, plend)
                    pg.append_line(lbegin, lend)
            else:
                if not emptyr:
                    in_line = True
                    plbegin = y
        if in_line and not emptyr:
            plend = pbottom
            lbegin, lend = pg.ppxl2norm(plbegin, plend)
            pg.append_line(lbegin, lend)
        pg.end_lines()

        pleft, ptop, pright, pbottom = apply(pg.norm2ppxl, pg.bbox())

        in_col = False

        pg.start_cols()
        for x in range(pleft, pright):
            ic = img.crop((x, ptop, x+1, pbottom))
            emptyc = is_empty(ic)
            if in_col:
                if emptyc:
                    in_col = False
                    pcend = x
                    cbegin, cend = pg.ppxl2norm(pcbegin, pcend)
                    pg.append_col(cbegin, cend)
            else:
                if not emptyc:
                    in_col = True
                    pcbegin = x
        if in_col and not emptyc:
            pcend = pright
            cbegin, cend = pg.ppxl2norm(pcbegin, pcend)
            pg.append_col(cbegin, cend)
        pg.end_cols()

        return pg

class PageColCondense(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
    def __call__(self, pg):
        cols = pg.cols
        iwcol = 0
        for i, col in enumerate(cols[1:]):
            if col.width() > cols[iwcol].width():
                iwcol = i

        pgleft, pgtop, pgright, pgbottom = pg.bbox()
        ifcol = -1
        fleft = cols[0].cbegin

        for i in range(iwcol-1, -1, -1):
            col = cols[i]
            cw = col.width()
            if col.ac > cw:
                ifcol = i
                fleft = col.cend + col.ac
                break

        for i in range(ifcol, -1, -1):
            col = cols[i]
            cbbox = col.bbox()
            ac = min(col.ac, col.width())
            cbbox[2] += ac
            img = pg.rcrop(cbbox)
            fleft -= cbbox[2] - cbbox[0]
            pg.rpaste(img, (fleft, pgtop))
            col.move_to(fleft)

        pg.rclear([0, 0, fleft, pg.height()])

        ilcol = len(cols)
        lright = cols[-1].cend

        for i in range(iwcol+1, len(cols)):
            col = cols[i]
            cw = col.width()
            if col.bc > cw:
                ilcol = i
                lright = col.cbegin - col.bc
                break

        for i in range(ilcol, len(cols)):
            col = cols[i]
            cbbox = col.bbox()
            bc = min(col.bc, col.width())
            cbbox[0] -= bc
            img = pg.rcrop(cbbox)
            pg.rpaste(img, (lright, pgtop))
            col.move_to(lright + bc)
            lright += cbbox[2] - cbbox[0]

        pg.rclear([lright, 0, pg.width(), pg.height()])

        pg.set_cols_bac()
        pg.parse_img_ref = None

        return pg

class PageLineCondense(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
    def __call__(self, pg):
        lines = pg.lines
        ihline = 0
        for i, line in enumerate(lines[1:]):
            if line.height() > lines[ihline].height():
                ihline = i

        pgleft, pgtop, pgright, pgbottom = pg.bbox()
        ifline = -1
        ftop = lines[0].lbegin

        for i in range(ihline-1, -1, -1):
            line = lines[i]
            lh = line.height()
            if line.al > lh:
                ifline = i
                ftop = line.lend + line.al
                break

        for i in range(ifline, -1, -1):
            line = lines[i]
            lbbox = line.bbox()
            al = min(line.al, line.height())
            lbbox[3] += al
            img = pg.rcrop(lbbox)
            ftop -= lbbox[3] - lbbox[1]
            pg.rpaste(img, (pgleft, ftop))
            line.move_to(ftop)

        pg.rclear([0, 0, pg.width(), ftop])

        illine = len(lines)
        lbottom = lines[-1].lend

        for i in range(ihline+1, len(lines)):
            line = lines[i]
            lh = line.height()
            if line.bl > lh:
                illine = i
                lbottom = line.lbegin - line.bl
                break

        for i in range(illine, len(lines)):
            line = lines[i]
            lbbox = line.bbox()
            bl = min(line.bl, line.height())
            lbbox[1] -= bl
            img = pg.rcrop(lbbox)
            pg.rpaste(img, (pgleft, lbottom))
            line.move_to(lbottom + bl)
            lbottom += lbbox[3] - lbbox[1]

        pg.rclear([0, lbottom, pg.width(), pg.height()])

        pg.set_lines_bal()
        pg.parse_img_ref = None

        return pg

class PageCrop(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
    def __call__(self, pg):
        img = pg.rcrop(pg.bbox())
        pg.render_img_ref = image.ImageRef(img)
        pg.lines = None
        pg.cols = None
        pg.parse_img_ref = None
        return pg

class PageInfo(PageConverter):
    all_targets = ('render_img',)
    all_targets_set = set(all_targets)
    def __init__(self, prefix='', *targets):
        PageConverter.__init__(self)
        self.prefix = prefix
        if len(targets) == 0:
            self.targets = self.all_targets
        else:
            for target in targets:
                assert(target in self.all_targets_set)
            self.targets = targets
    def render_img_info(self, pg):
        img = pg.render_img_ref.get_image()
        print self.prefix, img.mode, img.size
    def __call__(self, pg):
        for target in self.targets:
            func = getattr(self, target + '_info')
            func(pg)
        return pg

class PageCollector(PageConverter):
    def __init__(self):
        PageConverter.__init__(self)
        self.page_map = {}
        self.out_files = []
        self.output_prefix = "%s/out" % config.get_work_dir()
    def __call__(self, pg):
        img_ref = pg.render_img_ref
        img = img_ref.get_image()
        pn = pg.page_no
        out_file_name = '%s-%06d.png' % (self.output_prefix, pn)
        ncolors = image.image_colors(img)
        if ncolors == 2:
            img = img.convert('1')
        img.save(out_file_name)
        self.out_files.append(out_file_name)
        if not self.page_map.has_key(pn):
            self.page_map[pn] = len(self.out_files)
    def end(self, pgs, bk):
        for pg in pgs:
            self.__call__(pg)
        pm = self.page_map
        nopn = len(self.out_files)
        for pn in range(bk.last_page, bk.first_page, -1):
            if pm.has_key(pn):
                nopn = pm[pn]
            else:
                pm[pn] = nopn
        bk.img_files = self.out_files
        bk.page_map = self.page_map
        return []

class Book(object):
    def __init__(self):
        object.__init__(self)
