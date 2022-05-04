#!/usr/bin/env python
import shutil

destinationFolder = 'C://Program Files//Inkscape//share//inkscape//extensions//'
shutil.copyfile('.//unicorn.inx', destinationFolder + 'unicorn.inx')
shutil.copyfile('.//unicorn.py', destinationFolder + 'unicorn.py')
shutil.copyfile('.//unicorn//svg_parser.py', destinationFolder + 'unicorn//svg_parser.py')
shutil.copyfile('.//unicorn//entities.py', destinationFolder + 'unicorn//entities.py')
shutil.copyfile('.//unicorn//context.py', destinationFolder + 'unicorn//context.py')
input ('...')