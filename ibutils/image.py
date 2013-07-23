# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import tempfile
import Image, ImageFilter, ImageOps
import config

from util import *

class ImageRef(object):
    def __init__(self, image = None, file_name = None):
        object.__init__(self)
        self.image = image
        self.file_name = file_name
    def __del__(self):
        if self.file_name and os.path.exists(self.file_name):
            os.unlink(self.file_name)
    def clear_ref(self):
        self.file_name = None
        self.image = None
    def get_image(self):
        if self.image:
            return self.image
        elif self.file_name:
            self.image = Image.open(self.file_name)
            return self.image
    def get_file_name(self, ext = 'png'):
        if self.file_name:
            return self.file_name
        if self.image:
            self.file_name = temp_file_name('.'+ext, config.get_tmp_dir())
            self.image.save(self.file_name)
            return self.file_name
        assert(False)
    def dup(self):
        if self.image is not None:
            return ImageRef(self.image.copy())
        elif self.file_name:
            img = Image.open(self.file_name)
            return ImageRef(img)
        else:
            return ImageRef()

class AutoInvert(object):
    def __init__(self):
        object.__init__(self)
    def __call__(self, img_ref):
        img = img_ref.get_image()
        if img.mode == '1':
            img = ImageOps.grayscale(img)
        elif img.mode != 'L':
            return img_ref
        h = img.histogram()
        if sum(h[:64]) < img.size[0] * img.size[1] / 2:
            return img_ref
        img = ImageOps.invert(img)
        return ImageRef(img)

class Grayscale(object):
    def __init__(self):
        object.__init__(self)
    def __call__(self, img_ref):
        img = img_ref.get_image()
        if img.mode == 'L':
            return img_ref
        img = ImageOps.grayscale(img)
        return ImageRef(img)

class PreCrop(object):
    def __init__(self, trim_left, trim_top, trim_right, trim_bottom):
        object.__init__(self)
        self.trim_left = trim_left
        self.trim_top = trim_top
        self.trim_right = trim_right
        self.trim_bottom = trim_bottom
    def __call__(self, img_ref):
        if self.trim_left < 0.01 and self.trim_top < 0.01 and \
                self.trim_right < 0.01 and self.trim_bottom < 0.01:
            return img_ref
        img = img_ref.get_image().copy()
        iw, ih = img.size
        left = nround(self.trim_left * iw)
        right = iw - nround(self.trim_right * iw)
        top = nround(self.trim_top * ih)
        bottom = ih - nround(self.trim_bottom * ih)
        img.paste(255, (0, 0, iw, top))
        img.paste(255, (0, bottom, iw, ih))
        img.paste(255, (0, top, left, bottom))
        img.paste(255, (right, top, iw, bottom))
        return ImageRef(img)

class Unpaper(object):
    def __init__(self):
        object.__init__(self)
    def __call__(self, img_ref):
        out_file_name = temp_file_name('.png', config.get_tmp_dir())
        check_call(['unpaper', '-q', '--no-deskew',
                    img_ref.get_file_name(), out_file_name])
        return ImgRef(file_name = out_file_name)

class Gamma(object):
    def __init__(self, gamma):
        object.__init__(self)
        self.gamma = gamma
    def __call__(self, img_ref):
        if self.gamma < 0.001:
            return img_ref
        img = img_ref.get_image()
        if img.mode != 'L':
            return img_ref
        lut = [p * (p/255.0) ** self.gamma for p in range(256)]
        img = img.point(lut)
        return ImageRef(img)

def image_colors(img):
    h = img.histogram()
    colors = 0
    for p in h:
        if p > 0:
            colors += 1
    return colors

class ReduceColors(object):
    def __init__(self, ncolors):
        object.__init__(self)
        self.colors = ncolors
    def __call__(self, img_ref):
        if self.colors >= 256:
            return img_ref

        img = img_ref.get_image()
        if img.mode != 'L':
            return img_ref

        colors = image_colors(img)
        if colors <= self.colors:
            return img_ref

        out_file_name = temp_file_name('.png', config.get_tmp_dir())
        cmd = ['convert']
        scolors = '%d' % (self.colors,)
        cmd.extend(['-colors', scolors])
        cmd.extend(['-depth', '8', img_ref.get_file_name(), out_file_name])
        check_call(cmd)
        return ImageRef(file_name = out_file_name)

class FixBlackWhite(object):
    def __init__(self):
        object.__init__(self)
        fix_table = [g for g in range(256)]
        for g in range(10):
            fix_table[g] = 0
        for g in range(245, 256):
            fix_table[g] = 255
        self.fix_table = fix_table
    def __call__(self, img_ref):
        img = img_ref.get_image()
        if img.mode != 'L':
            return img_ref
        img = img_ref.get_image()
        img = img.point(self.fix_table)
        return ImageRef(img)
