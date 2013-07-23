# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import argparse

from . import *

def parse_args():
    parser = argparse.ArgumentParser(description='Convert image book')
    parser.add_argument('--trim-left', type=str2percent, default=0.)
    parser.add_argument('--trim-top', type=str2percent, default=0.)
    parser.add_argument('--trim-right', type=str2percent, default=0.)
    parser.add_argument('--trim-bottom', type=str2percent, default=0.)
    parser.add_argument('-f', '--first-page', type=int, default=1)
    parser.add_argument('-l', '--last-page', type=int)
    parser.add_argument('input_file', help='input file name')
    parser.add_argument('output_file', help='output file name')

    args = parser.parse_args()
    return args

def condense():
    args = parse_args()

    do_convert(args.input_file, args.output_file,
               args.first_page, args.last_page,
               # converters
               r(auto_invert()),
               r2p(),
               p(grayscale()),
               bbox(args.trim_left, args.trim_top,
                             args.trim_right, args.trim_bottom),
               parser(),
               col_condense(),
               line_condense(),
               collector(),
               )

def main():
    condense()
