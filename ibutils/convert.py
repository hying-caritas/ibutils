# Copyright 2013 Huang Ying <huang.ying.caritas@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


import os.path

import config
import page
from util import *

import pdf.info
import pdf.to_image
import pdf.generator
import djvu.info
import djvu.to_image
import imb.info
import imb.to_image
import imb.generator

supported_input_formats = set(('pdf', 'imb', 'djvu'))
supported_output_formats = set(('pdf', 'imb'))

def file_format(file_name):
    s, fmt = os.path.splitext(file_name)
    fmt = fmt.lstrip('.')
    return fmt

def parse_input_info(input_format, input_file):
    if input_format == 'pdf':
        info_parser = pdf.info.PDFInfoParser(input_file)
    elif input_format == 'imb':
        info_parser = imb.info.ImbInfoParser(inpput_file)
    elif input_format == 'djvu':
        info_parser = djvu.info.DJVUInfoParser(input_file)
    return info_parser.parse()

def create_input_to_image(input_file, input_format):
    if input_format == 'pdf':
        return pdf.to_image.PDFImage(input_file)
    elif input_format == 'imb':
        return imb.to_image.IMBToImage(input_file)
    elif input_format == 'djvu':
        return djvu.to_image.DJVUToImage(input_file)

def create_generator(out_format):
    if out_format == 'imb':
        return imb.generator.IMBGenerator()
    elif out_format == 'pdf':
        return pdf.generator.PDFGenerator()

def do_convert(input_file, output_file, first_page, last_page, *converters):
    input_format = file_format(input_file)
    error_exit_if(input_format not in supported_input_formats,
                  "Unsupported input file format, supported formats: %s.\n" %
                  " ".join([f for f in supported_input_formats]))

    output_format = file_format(output_file)
    error_exit_if(output_format not in supported_output_formats,
                  "Unsupported output file format, supported formats: %s.\n" %
                  " ".join([f for f in supported_output_formats]))

    bk = page.Book()

    meta, bms = parse_input_info(input_format, input_file)
    bk.title = meta.doc_title
    bk.author = meta.author
    bk.first_page = first_page
    bk.last_page = meta.pages
    bk.bookmarks = bms

    if last_page:
        bk.last_page = last_page

    input_to_image = create_input_to_image(input_file, input_format)
    gen = create_generator(output_format)

    for pn in range(bk.first_page, bk.last_page+1):
        print 'page: %d' % (pn,)

        img_ref = input_to_image.to_image(pn)
        pg = page.Page(bk, pn, img_ref)

        for converter in converters:
            pg = converter(pg)
            if pg is None:
                break

    pgs = []
    for converter in converters:
        pgs = converter.end(pgs, bk)

    gen.generate(output_file, bk)

    config.clean_work_dir()
