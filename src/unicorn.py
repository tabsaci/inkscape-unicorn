#!/usr/bin/env python
'''
Copyright (c) 2010 MakerBot Industries

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''
import sys,os
import inkex
from math import *
import getopt
from unicorn.context import GCodeContext
from unicorn.svg_parser import SvgParser

class MyEffect(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
    self.arg_parser.add_argument("--delay",
                      action="store", type=float,
                      dest="delay", default="20.0",
                      help="Delay after laser on/off command before movement in milliseconds")
    self.arg_parser.add_argument("--goHome",
                      action="store", type=str,
                      dest="goHome", default="false",
                      help="Autohome, and go to xyz offset before starting")
    self.arg_parser.add_argument("--xyz-speed",
                      action="store", type=float,
                      dest="xyz_speed", default="350.0",
                      help="XYZ axes speed in mm/min")
    self.arg_parser.add_argument("--travel-speed",
                      action="store", type=float,
                      dest="travel_speed", default="6000.0",
                      help="Travel speed in mm/min")
    self.arg_parser.add_argument("--x-offset",
                      action="store", type=float,
                      dest="x_offset", default="54.0",
                      help="Starting X position")
    self.arg_parser.add_argument("--y-offset",
                      action="store", type=float,
                      dest="y_offset", default="14.0",
                      help="Starting Y position")
    self.arg_parser.add_argument("--z-offset",
                      action="store", type=float,
                      dest="z_offset", default="95.0",
                      help="Starting Z position")
    self.arg_parser.add_argument("--num-runs",
                      action="store", type=int,
                      dest="num_runs", default="1",
                      help="Number of repeating the drawing process")
    self.arg_parser.add_argument("--tab",
                      action="store", type=str,
                      dest="tab")

  def has_changed(self, ret):
    return True

  def save(self, stream):
    self.context.generate(stream)

  def effect(self):
    self.context = GCodeContext(
                           self.options.xyz_speed, 
                           self.options.travel_speed,
                           self.options.delay,
                           self.options.goHome == 'true',
                           self.options.x_offset,
                           self.options.y_offset,
                           self.options.z_offset,
                           self.options.num_runs,
                           self.options.input_file)
    parser = SvgParser(self.document.getroot())
    parser.parse()
    for entity in parser.entities:
      entity.get_gcode(self.context)

if __name__ == '__main__':   #pragma: no cover
  e = MyEffect()
  e.run()
