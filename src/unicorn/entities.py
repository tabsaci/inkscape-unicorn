from math import cos, sin, radians, sqrt
import pprint

epsilon = 0.0000001

class Entity:
	def get_gcode(self,context):
		raise NotImplementedError()

class Point:
	def __init__ (self, x, y):
		self.x = x
		self.y = y

	def __getitem__ (self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		raise IndexError ()

	def __str__ (self):
		return "[%.5f, %.5f]" % (self.x, self.y)

	def IsNear (self, other):
		return abs (self.x - other.x) < epsilon and abs (self.y - other.y) < epsilon

	def distanceSquare (self, point):
		return (self.x - point.x)**2 + (self.y - point.y)**2

	def distance (self, point):
		return sqrt (self.distanceSquare (point))

class Line(Entity):
	def __init__(self, start, end):
		self.start = Point (start[0], start[1])
		self.end = Point (end[0], end[1])

	def __str__(self):
		return "Line from " + str (self.start) + " to " + str (self.end)

	def get_gcode(self,context):
		"Emit gcode for drawing line"
		context.codes.append("(" + str(self) + ")")
		context.go_to_point(self.start[0],self.start[1])
		context.draw_to_point(self.end[0],self.end[1])
		context.codes.append("")

	def get_intersection_with_line (self, line):
		# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
		x1 = self.start.x
		y1 = self.start.y
		x2 = self.end.x
		y2 = self.end.y
		x3 = line.start.x
		y3 = line.start.y
		x4 = line.end.x
		y4 = line.end.y
		resx = (x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)
		resy = (x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)
		d = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
		if d == 0:
			return None
		return Point (resx / d, resy / d)

	def get_intersections_with_line_segments (self, lineSegments):
		result = []
		for lineSegment in lineSegments:
			intersection = self.get_intersection_with_line (lineSegment)
			if intersection is not None and lineSegment.is_point_on_line (intersection) and self.is_point_on_line (intersection):
				result.append (intersection)
		return result

	def is_point_on_line (self, point):
		#https://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment
		crossproduct = (point.y - self.start.y) * (self.end.x - self.start.x) - (point.x - self.start.x) * (self.end.y - self.start.y)
		# compare versus epsilon for floating point values, or != 0 if using integers	
		if abs(crossproduct) > epsilon:
			return False
		dotproduct = (point.x - self.start.x) * (self.end.x - self.start.x) + (point.y - self.start.y)*(self.end.y - self.start.y)
		if dotproduct < 0:
			return False
		squaredlengthba = self.end.distanceSquare (self.start)
		if dotproduct - squaredlengthba > epsilon:
			return False
		return True

	def get_length (self):
		return self.start.distance (self.end)


class Circle(Entity):
	def __str__(self):
		return "Circle at [%.2f,%.2f], radius %.2f" % (self.center[0], self.center[1], self.radius)

	def get_gcode(self,context):
		"Emit gcode for drawing circle"
		start = (self.center[0] - self.radius, self.center[1])
		arc_code = "G3 I%.2f J0 F%.2f" % (self.radius, context.xy_feedrate)

		context.codes.append("(" + str(self) + ")")
		context.go_to_point(start[0],start[1])
		context.start()
		context.codes.append(arc_code)
		context.stop()
		context.codes.append("")

class Arc(Entity):
	def __str__(self):
		return "Arc at [%.2f, %.2f], radius %.2f, from %.2f to %.2f" % (self.center[0], self.center[1], self.radius, self.start_angle, self.end_angle)

	def find_point(self,proportion):
		"Find point at the given proportion along the arc."
		delta = self.end_angle - self.start_angle
		angle = self.start_angle + delta*proportion
		
		return (self.center[0] + self.radius*cos(angle), self.center[1] + self.radius*sin(angle))

	def get_gcode(self,context):
		"Emit gcode for drawing arc"
		start = self.find_point(0)
		end = self.find_point(1)

		arc_code = "G3 X%.2f Y%.2f I%.2f J%.2f F%.2f" % (end[0], end[1], self.center[0] - start[0], self.center[1] - start[1], context.xy_feedrate)

		context.codes.append("(" + str(self) + ")")
		context.go_to_point(start[0],start[1])
		context.start()
		context.codes.append(arc_code)
		context.stop()
		context.codes.append("")

class Ellipse(Entity):	#TODO - NOT YET IMPLEMENTED
	def __str__(self):
		return "Ellipse at [%.2f, %.2f], major [%.2f, %.2f], minor/major %.2f" + " start %.2f end %.2f" % \
		(self.center[0], self.center[1], self.major[0], self.major[1], self.minor_to_major, self.start_param, self.end_param)

class PolyLine(Entity):
	def __str__(self):
		return "Polyline consisting of %d segments." % len(self.segments)

	def get_gcode(self, context):
		"Emit gcode for drawing polyline"
		if hasattr (self, 'segments'):
			self.draw_countour (context)
		if hasattr (self, 'withFill') and self.withFill:
			self.draw_fill (context)

	def draw_countour (self, context):
		for points in self.segments:
			context.codes.append("(" + str(self) + ")")
			context.go_to_point(points[0][0],points[0][1])
			context.start()
			for point in points[1:]:
				context.draw_to_point(point[0],point[1])
			context.stop()
			context.codes.append("")

	def draw_fill (self, context):
		fillLines = self.get_horizontal_fill_lines (self.segments[0], 0.4) # TODO hardcoded gap
		contourLines = self.get_contour_lines (self.segments)
		refPointAtStart = True
		for fillLine in fillLines:
			intersections = fillLine.get_intersections_with_line_segments (contourLines)

			refpoint = fillLine.end
			if refPointAtStart:
				refpoint = fillLine.start
				refPointAtStart = False
			else:
				refPointAtStart = True
			intersections.sort (key = lambda p: refpoint.distanceSquare (p))

			if len (intersections) % 2 != 0:
				message = "Unprocessed intersection(s): "
				for intersection in intersections:
					message += str (intersection)
				print (message)
				continue

			for index in range (0, int (len (intersections) / 2.0)):
				indexStart = index * 2
				linePart = Line (intersections[indexStart], intersections[indexStart + 1])
				linePart.get_gcode (context)

	def get_contour_lines (self, segments):
		lines = []
		for segment in segments:
			for pointIndex in range (1, len (segment)):
				lineCandidate = Line (segment[pointIndex - 1], segment[pointIndex])
				if lineCandidate.get_length () > epsilon:
					lines.append (lineCandidate)
		return lines

	def get_horizontal_fill_lines (self, points, gap):
		ymin = min (points, key = lambda point: point[1])[1]
		ymax = max (points, key = lambda point: point[1])[1]
		xmin = min (points, key = lambda point: point[0])[0]
		xmax = max (points, key = lambda point: point[0])[0]
		lines = []
		while ymin < ymax:
			lines.append (Line ((xmin - 1, ymin), (xmax + 1, ymin)))
			ymin += gap
		return lines

class TestRect (Entity):
	def __str__(self):
		thisStr =  "TestRect with bottom left at [%.2f, %.2f] and size %.2fx%.2f" % (self.bottom, self.left, self.width, self. height)
		if self.laserIntensity is not None:
			thisStr += ", laser intensity at " + str (self.laserIntensity)
		else:
			thisStr += ", laser intensity at full"

		if self.contour is True:
			thisStr += ", countour only"
		else:
			thisStr += ", filled with " + str (self.fillDensity) + " density";
		
		return thisStr

	def __init__(self, bottom, left, speed, width, height, contour, fillDensity, laserIntensity):
		self.speed = speed
		self.bottom = bottom
		self.left = left
		self.width = width
		self.height = height
		self.contour = contour
		self.fillDensity = fillDensity
		self.laserIntensity = laserIntensity

	def get_gcode(self, context):
		context.xyz_speed = self.speed
		context.setLaserIntensity (self.laserIntensity)

		context.codes.append("(" + str(self) + ")")
		context.go_to_point (self.left, self.bottom)
		if self.contour:		
		  context.draw_to_point (context.getX ()				, context.getY () + self.height)
		  context.draw_to_point (context.getX () + self.width	, context.getY ())
		  context.draw_to_point (context.getX ()				, context.getY () - self.height)
		  context.draw_to_point (context.getX () - self.width	, context.getY ())
		if self.fillDensity is not None:
		  targetY = context.getY () + self.height
		  while context.getY () < targetY - self.fillDensity:
		    context.go_to_point (self.left, context.getY () + self.fillDensity)
		    context.draw_to_point (context.getX () + self.width, context.getY ())
		context.stop ()
		context.codes.append("")
		

