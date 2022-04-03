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
    self.arg_parser.add_argument("--start-delay",
                      action="store", type=float,
                      dest="start_delay", default="20.0",
                      help="Delay after pen down command before movement in milliseconds")
    self.arg_parser.add_argument("--stop-delay",
                      action="store", type=float,
                      dest="stop_delay", default="20.0",
                      help="Delay after pen up command before movement in milliseconds")
    self.arg_parser.add_argument("--xyz-speed",
                      action="store", type=float,
                      dest="xyz_speed", default="100.0",
                      help="XYZ axes speed in mm/min")
    self.arg_parser.add_argument("--z-height",
                      action="store", type=float,
                      dest="z_height", default="0.0",
                      help="Z axis print height in mm")
    self.arg_parser.add_argument("--x-home",
                      action="store", type=float,
                      dest="x_home", default="0.0",
                      help="Starting X position")
    self.arg_parser.add_argument("--y-home",
                      action="store", type=float,
                      dest="y_home", default="0.0",
                      help="Starting Y position")
    self.arg_parser.add_argument("--num-runs",
                      action="store", type=int,
                      dest="num_runs", default="1")
    self.arg_parser.add_argument("--tab",
                      action="store", type=str,
                      dest="tab")

  def has_changed(self, ret):
    return True

  def save(self, stream):
    self.context.generate(stream)

  def effect(self):
    self.context = GCodeContext(self.options.xyz_speed, 
                           self.options.start_delay, self.options.stop_delay,
                           self.options.z_height,
                           self.options.x_home, self.options.y_home,
                           self.options.num_runs,
                           self.options.input_file)
    parser = SvgParser(self.document.getroot())
    parser.parse()
    for entity in parser.entities:
      entity.get_gcode(self.context)

if __name__ == '__main__':   #pragma: no cover
  e = MyEffect()
  e.run()
