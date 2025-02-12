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
import sys
import os
from unicorn.entities import TestRect
from unicorn.context import GCodeContext

def GetTestContext (goHome):
  context = GCodeContext (
    xyz_speed = 350,
    travel_speed = 6000,
    delay = 20, 
    goHome = goHome,
    x_offset = 54,
    y_offset = 14,
    z_offset = 95,
    num_runs = 1,
    comment = None)
  return context

def GenerateSpeedTest (output, count, width, height, gap, speedFrom, speedTo):
  """Generates 'count' number of rects next to each other on the x axis
     with 'width'x'height' size, and 'gap' distance among them.
     The first rect will be engraved with 'speedFrom' speed, the last will be with 'speedTo' speed
     all the others will have speed distributed lineary between these""" 
  left = 0
  actSpeed = speedFrom
  rects = []
  for index in range (count):
    rects.append (TestRect (0, left, actSpeed, width, height, True, None, None)) # bottom, left, speed, width, height, contourOnly, fillDensity, laserIntensity
    left += width + gap
    actSpeed += (speedTo - speedFrom) / (count - 1) 
  GenerateCustomRectsTest (output, gap, rects)


def GenerateFillDensityTest (output, count, width, height, gap, speed, densityFrom, densityTo):
  """Generates 'count' number of rects next to each other on the x axis
     with 'width'x'height' size, 'speed' speed and 'gap' distance among them.
     The first rect will be filled with line that are 'densityFrom' distance from each other, 
     the last will be with filled with lines 'densityTo' distance from each other
     all the others will have the distance distributed lineary between these""" 
  left = 0
  actDensity = densityFrom
  rects = []
  for index in range (count):
    rects.append (TestRect (15, left, speed, width, height, False, actDensity, None))
    left += width + gap
    actDensity += (densityTo - densityFrom) / (count - 1) 
  GenerateCustomRectsTest (output, gap, rects)


def GenerateLaserIntensityTest (output, count, width, height, gap, speed, density, intensityFrom, intensityTo):
  """Generates 'count' number of rects next to each other on the x axis
     with 'width'x'height' size, 'speed' speed and 'gap' distance among them.
     The rects will be filled with lines that are 'density' distance from each other.
     The first rect will be engraved with the laser set to 'intensityFrom', 
     the last will be with engraved with laser set to 'intensityTo', 
     all the others will have the lasers intensity distributed lineary between these""" 
  left = 0
  actIntensity = intensityFrom
  rects = []
  for index in range (count):
    rects.append (TestRect (30, left, speed, width, height, True, density, actIntensity))
    left += width + gap
    actIntensity += (intensityTo - intensityFrom) / (count - 1) 
  GenerateCustomRectsTest (output, gap, rects)


def GenerateCustomRectsTest (output, gap, rects):
  left = 0
  context = GetTestContext (False)
  for rect in rects:
    rect.get_gcode (context)
    left += rect.width + gap
  with open (output, 'wb') as stream:  
    context.generate (stream)


def GenerateTestScripts ():
  folderPath = os.path.dirname (os.path.realpath (__file__))

  speedTestFilePath = os.path.join (folderPath, "speedTest.gcode")
  GenerateSpeedTest (
    output = speedTestFilePath, 
    count = 9, 
    width = 10,
    height = 10,
    gap = 2,
    speedFrom = 100,
    speedTo = 500)

  fillDensityTestFilePath = os.path.join (folderPath, "fillDensityTest.gcode")
  GenerateFillDensityTest (
    output = fillDensityTestFilePath, 
    count = 9, 
    width = 10,
    height = 10,
    gap = 2,
    speed = 350,
    densityFrom = 0.4,
    densityTo = 1.2)

  laserIntensityTestFilePath = os.path.join (folderPath, "laserIntensityTest.gcode")
  GenerateLaserIntensityTest (
    output = laserIntensityTestFilePath, 
    count = 9, 
    width = 10,
    height = 10,
    gap = 2,
    speed = 350,
    density = 1.0,
    intensityFrom = 10,
    intensityTo = 250)

  customRectsTestFilePath = os.path.join (folderPath, "customRectsTest.gcode")
  GenerateCustomRectsTest (
    output = customRectsTestFilePath, 
    gap = 20, 
    rects = [
      TestRect (
        bottom = 30, 
        left = 0,
        speed = 350,
        width = 10,
        height = 15,
        contourOnly = False,
        fillDensity = 1.1,
        laserIntensity = 255)
    ])


def CutTest (gap, numRunsFrom, numRunsTo, zOffsetFrom, zOffsetTo, count, speed):
  context = GetTestContext (True)
  zStep = 0.0
  if count > 1:
    zStep = (zOffsetTo - zOffsetFrom) / (count - 1) 
  actZ = 0
  actLeft = 0
  actBottom = 50
  for numRunsIndex in range (numRunsFrom, numRunsTo + 1): # the rows - each row, different runNum
    for zOffsetIndex in range (count): # the columns - each column, different zOffset
      rect = TestRect (
        bottom = actBottom, 
        left = actLeft,
        speed = speed,
        width = 10,
        height = 10,
        contour = True,
        fillDensity = None,
        laserIntensity = 255)
      for i in range (numRunsIndex): # the runs, with modified Z offset in each run
        context.go_to_z (actZ)
        rect.get_gcode (context)
        actZ -= zOffsetFrom + zOffsetIndex * zStep
      actLeft += rect.width + gap
      actZ = 0
    actLeft = 0
    actBottom += rect.height + gap

  folderPath = os.path.dirname (os.path.realpath (__file__))
  filePath = os.path.join (folderPath, "cutTest.gcode")
  with open (filePath, 'wb') as stream:  
    context.generate (stream)




if __name__ == '__main__':
  #GenerateTestScripts ()
  CutTest (
    gap = 2,
    numRunsFrom = 6,
    numRunsTo = 6,
    zOffsetFrom = 1,
    zOffsetTo = 1,
    count = 1,
    speed = 70)

