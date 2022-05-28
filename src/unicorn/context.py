from math import *
import sys

class GCodeContext:
    def __init__(self, xyz_speed, travel_speed, delay, goHome, x_offset, y_offset, z_offset, num_runs, comment):
      self.xyz_speed = xyz_speed
      self.travel_speed = travel_speed
      self.delay = delay
      self.x_offset = 0.0
      self.y_offset = 0.0
      self.z_offset = 0.0
      if (goHome):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.z_offset = z_offset
      self.num_runs = num_runs
      
      self.drawing = False
      self.actPosition = (self.x_offset, self.y_offset, self.z_offset)

      self.setLaserIntensity (255)
      self.endCommand = "M107"

      self.preamble = []      
      if comment != None:
        self.preamble += [ "( %s )" % (comment.encode ("ascii", "ignore")) ]
      parameterList = " ".join (sys.argv)
      parameterList = parameterList.encode ("ascii", "ignore")
      self.preamble += [
        "( Generation parameters: %s )" % parameterList,
        "G21 (metric ftw)",
        "G90 (absolute mode)",
        "G0 F%0.2F (set speed for travel)" % (self.travel_speed),
        ""
      ]

      if goHome:
        self.preamble += [
          "G28 ; Home all axes",
          "G0 X%0.2F Y%0.2F Z%0.2F (go to start point)" % (self.x_offset, self.y_offset, self.z_offset),
          "M0 Turn on laser to set the focus point",
          self.startCommand,
          "M0 Set focus point of the laser",
          self.endCommand,
          "M0 Put on the actual workpiece"
        ]
      else:
        self.preamble += [
          "G92 X%.2f Y%.2f Z%.2f (you are here)" % (self.x_offset, self.y_offset, self.z_offset)
        ]
      self.preamble += [ "" ]

      self.postscript = [
        "",
		"(end of print job)",
		self.endCommand,
		"G4 P%d (wait %dms)" % (self.delay, self.delay),
		"M300 S255 (turn off servo)",
        "G0 F%.2f" % (self.travel_speed),
        "G0 X%0.2F Y%0.2F Z%0.2F (go to start point)" % (self.x_offset, self.y_offset, self.z_offset),
		"M18 (drives off)",
      ]

      self.codes = []

    def generate(self, stream):
      for line in self.preamble:
          stream.write ((line + '\n').encode ('ascii'))
      for p in range(0,self.num_runs):
        for line in self.codes:
          stream.write ((line + '\n').encode ('ascii'))
      for line in self.postscript:
          stream.write ((line + '\n').encode ('ascii'))
  
    def setLaserIntensity (self, laserIntensity):
      if laserIntensity is None or laserIntensity < 0 or laserIntensity >= 255:
        self.startCommand = "M106"
      elif laserIntensity == 0:
        raise ValueError ()
      else:
        self.startCommand = "M106 S%d"  % (laserIntensity)

    def start (self):
      self.codes.append (self.startCommand)
      self.codes.append ("G4 P%d (wait %dms)" % (self.delay, self.delay))
      self.drawing = True

    def stop (self):
      self.codes.append (self.endCommand)
      self.codes.append ("G4 P%d (wait %dms)" % (self.delay, self.delay))
      self.drawing = False

    def getX (self) -> float:
      if self.actPosition is None:
        return None
      return self.actPosition[0]

    def getY (self) -> float:
      if self.actPosition is None:
        return None
      return self.actPosition[1]

    def getZ (self) -> float:
      if self.actPosition is None:
        return None
      return self.actPosition[2]

    def isAt (self, x, y, z):
      if self.actPosition is None or x is None or y is None or z is None:
        return False
      xEqual = round (self.getX (), 2) == round (x, 2)
      yEqual = round (self.getY (), 2) == round (y, 2)
      zEqual = round (self.getZ (), 2) == round (z, 2)
      return xEqual and yEqual and zEqual

    def go_to_z (self, z):
      if self.isAt (self.getX (), self.getY (), z):
        return
      if self.drawing: 
        self.stop ()
      self.codes.append ("G1 Z%.2f" % (self.z_offset + z)) 
      self.actPosition = (self.getX (), self.getY (), z)

    def go_to_point (self, x, y):
      if self.isAt (x, y, self.getZ ()):
        return
      if self.drawing: 
        self.stop ()
      self.codes.append("G1 X%.2f Y%.2f F%.2f" % (self.x_offset + x, self.y_offset + y, self.travel_speed)) 
      self.actPosition = (x, y, self.getZ ())

    def draw_to_point (self, x, y):
      if self.isAt (x, y, self.getZ ()):
        return
      if self.drawing == False:
        self.start ()
      self.codes.append("G1 X%0.2f Y%0.2f F%0.2f" % (self.x_offset + x, self.y_offset + y, self.xyz_speed))
      self.actPosition = (x, y, self.getZ ())
