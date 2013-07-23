# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import image
import page
from convert import do_convert
from util import *

r = page.PageRenderConverter
r2p = page.PageRenderToParse
p = page.PageParseConverter
bbox = page.PageBBox
parser = page.PageParser
col_condense = page.PageColCondense
line_condense = page.PageLineCondense
collector = page.PageCollector

auto_invert = image.AutoInvert
grayscale = image.Grayscale
