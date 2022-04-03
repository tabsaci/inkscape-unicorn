from math import *
import sys

class GCodeContext:
    def __init__(self, xyz_speed, delay, z_height, x_home, y_home, num_runs, file):
      self.xyz_speed = xyz_speed
      self.delay = delay
      self.z_height = z_height
      self.x_home = x_home
      self.y_home = y_home
      self.num_runs = num_runs
      self.file = file
      
      self.drawing = False
      self.actPosition = None

      self.preamble = [
        "(Scribbled version of %s @ %.2f)" % (self.file, self.xyz_speed),
        "( %s )" % " ".join(sys.argv),
        "G21 (metric ftw)",
        "G90 (absolute mode)",
        "G92 X%.2f Y%.2f Z%.2f (you are here)" % (self.x_home, self.y_home, self.z_height),
        ""
      ]

      self.startCommand = "M106"
      self.endCommand = "M107"

      self.postscript = [
        "",
		"(end of print job)",
		self.endCommand,
		"G4 P%d (wait %dms)" % (self.delay, self.delay),
		"M300 S255 (turn off servo)",
		"G1 X0 Y0 F%0.2F" % self.xyz_speed,
		"G1 X%0.2F Y%0.2F F%0.2F (go home)" % (self.x_home, self.y_home, self.xyz_speed),
		"M18 (drives off)",
      ]

      self.codes = []

    def generate(self, stream):
      codesets = [self.preamble]
      codesets.append(self.codes)

      for p in range(0,self.num_runs):
        for codeset in codesets:
          for line in codeset:
            stream.write ((line + '\n').encode ('ascii'))
        for line in self.postscript:
            stream.write ((line + '\n').encode ('ascii'))

    def start(self):
      self.codes.append(self.startCommand)
      self.codes.append("G4 P%d (wait %dms)" % (self.delay, self.delay))
      self.drawing = True

    def stop(self):
      self.codes.append(self.endCommand)
      self.codes.append("G4 P%d (wait %dms)" % (self.delay, self.delay))
      self.drawing = False

    def go_to_point(self, x, y, stop=False):
      if self.actPosition == (x,y):
        return
      if stop:
        return
      else:
        if self.drawing: 
            self.stop ()
        self.codes.append("G1 X%.2f Y%.2f F%.2f" % (x,y, self.xyz_speed))
      self.actPosition = (x,y)
	
    def draw_to_point(self, x, y, stop=False):
      if self.actPosition == (x,y):
          return
      if stop:
        return
      else:
        if self.drawing == False:
            self.start ()
        self.codes.append("G1 X%0.2f Y%0.2f F%0.2f" % (x,y, self.xyz_speed))
      self.actPosition = (x,y)
