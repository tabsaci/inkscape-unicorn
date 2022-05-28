import inkex, cubicsuperpath, simplepath, simplestyle, cspsubdiv
from simpletransform import *
from bezmisc import *
import unicorn.entities
from math import radians
from lxml import etree
import sys, pprint

def parseLengthWithUnits( str ):
  '''
  Parse an SVG value which may or may not have units attached
  This version is greatly simplified in that it only allows: no units,
  units of px, mm, and units of %.  Everything else, it returns None for.
  There is a more general routine to consider in scour.py if more
  generality is ever needed.
  '''
  u = 'px'
  s = str.strip()
  if s[-2:] == 'px':
    s = s[:-2]
  if s[-2:] == 'mm':
    u = 'mm'
    s = s[:-2]
  if s[-2:] == 'cm':
    u = 'cm'
    s = s[:-2]
  elif s[-1:] == '%':
    u = '%'
    s = s[:-1]
  try:
    v = float( s )
  except:
    return None, None
  return v, u

def subdivideCubicPath( sp, flat, i=1 ):
  """
  Break up a bezier curve into smaller curves, each of which
  is approximately a straight line within a given tolerance
  (the "smoothness" defined by [flat]).

  This is a modified version of cspsubdiv.cspsubdiv(). I rewrote the recursive
  call because it caused recursion-depth errors on complicated line segments.
  """

  while True:
    while True:
      if i >= len( sp ):
        return

      p0 = sp[i - 1][1]
      p1 = sp[i - 1][2]
      p2 = sp[i][0]
      p3 = sp[i][1]

      b = ( p0, p1, p2, p3 )

      if cspsubdiv.maxdist( b ) > flat:
        break

      i += 1

    one, two = beziersplitatt( b, 0.5 )
    sp[i - 1][2] = one[1]
    sp[i][0] = two[2]
    p = [one[2], one[3], two[1]]
    sp[i:1] = [p]

class SvgIgnoredEntity:
  def load(self,node,mat):
    self.tag = node.tag
  def __str__(self):
    return "Ignored '%s' tag" % self.tag
  def get_gcode(self,context):
    #context.codes.append("(" + str(self) + ")")
    #context.codes.append("")
    return

class SvgPath(unicorn.entities.PolyLine):
  def load(self, node, mat):
    d = node.get('d')
    if len(inkex.Path(d).to_arrays()) == 0:
      return
    p = inkex.paths.CubicSuperPath(inkex.paths.Path(d))
    p = p.transform(mat)

    # p is now a list of lists of cubic beziers [ctrl p1, ctrl p2, endpoint]
    # where the start-point is the last point in the previous segment
    self.segments = []
    for sp in p:
      points = []
      subdivideCubicPath(sp,0.2)  # TODO: smoothness preference
      for csp in sp:
        points.append((csp[1][0],csp[1][1]))
      self.segments.append(points)

  def new_path_from_node(self, node):
    newpath = etree.Element(inkex.addNS('path','svg'))
    s = node.get('style')
    if s:
      newpath.set('style',s)
    t = node.get('transform')
    if t:
      newpath.set('transform',t)
    return newpath

class SvgRect(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    x = float (node.get ('x'))
    y = float (node.get ('y'))
    w = float (node.get ('width'))
    h = float (node.get ('height'))
    rx = 0.0
    if node.get ('rx') != None:
      rx = float (node.get ('rx'))
    ry = 0.0
    if node.get ('ry') != None:
      ry = float (node.get ('ry'))

    a = []
    a.append(['M', [x + rx          , y]])
    a.append(['l', [w - 2 * rx      , 0]])
    a.append(['c', [rx, 0, rx, 0, rx, ry]])
    a.append(['l', [0               , h - 2 * ry]])
    a.append(['c', [0, ry, 0, ry, -rx, ry]])
    a.append(['l', [-(w - 2 * rx)   , 0]])
    a.append(['c', [-rx, 0, -rx, 0, -rx, -ry]])
    a.append(['l', [0               , -(h - 2 * ry)]])
    a.append(['c', [0, -ry, 0, -ry, rx, -ry]])
    a.append(['Z', []])
    print (str(Path(a)))
    newpath.set('d', str(Path(a)))
    SvgPath.load(self,newpath,mat)

class SvgLine(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    x1 = float(node.get('x1'))
    y1 = float(node.get('y1'))
    x2 = float(node.get('x2'))
    y2 = float(node.get('y2'))
    a = []
    a.append(['M', [x1,y1]])
    a.append(['L', [x2,y2]])
    newpath.set('d', str(Path(a)))
    SvgPath.load(self,newpath,mat)

class SvgPolyLine(SvgPath):
  def load(self, node, mat):
    newpath = self.new_path_from_node(node)
    pl = node.get('points','').strip()
    if pl == '':
      return
    pa = pl.split()
    if not len(pa):
      return

    d = "M " + pa[0]
    for i in range(1, len(pa)):
      d += " L " + pa[i]
    newpath.set('d',d)
    SvgPath.load(self,newpath,mat)

class SvgEllipse(SvgPath):
  def load(self, node,mat):
    rx = float(node.get('rx','0'))
    ry = float(node.get('ry','0'))
    SvgPath.load(self,self.make_ellipse_path(rx,ry,node), mat)
  def make_ellipse_path(self, rx, ry, node):
    if rx == 0 or ry == 0:
      return None
    cx = float(node.get('cx','0'))
    cy = float(node.get('cy','0'))
    x1 = cx - rx
    x2 = cx + rx
    d = 'M %f,%f ' % (x1,cy) + \
      'A %f,%f ' % (rx,ry) + \
      '0 1 0 %f, %f ' % (x2,cy) + \
      'A %f,%f ' % (rx,ry) + \
      '0 1 0 %f,%f' % (x1,cy)
    newpath = self.new_path_from_node(node)
    newpath.set('d',d)
    return newpath
  
class SvgCircle(SvgEllipse):
  def load(self, node,mat):
    rx = float(node.get('r','0'))
    SvgPath.load(self,self.make_ellipse_path(rx,rx,node), mat)

class SvgText(SvgIgnoredEntity):
  def load(self,node,mat):    # Note: empty text also raises warning
    inkex.errormsg('Warning: unable to draw text. please convert it to a path first.')
    SvgIgnoredEntity.load(self,node,mat)

class SvgParser:

  entity_map = {
    'path': SvgPath,
    'rect': SvgRect,
    'line': SvgLine,
    'polyline': SvgPolyLine,
    'polygon': SvgPolyLine,
    'circle': SvgCircle,
    'ellipse': SvgEllipse,
    'pattern': SvgIgnoredEntity,
    'metadata': SvgIgnoredEntity,
    'defs': SvgIgnoredEntity,
    'eggbot': SvgIgnoredEntity,
    ('namedview','sodipodi'): SvgIgnoredEntity,
    'text': SvgText
  }

  def __init__(self, svg):
    self.svg = svg
    self.entities = []

  def getLength( self, name, default ):
    '''
    Get the <svg> attribute with name "name" and default value "default"
    Parse the attribute into a value and associated units.  Then, accept
    no units (''), units of pixels ('px'), and units of percentage ('%').
    '''
    str = self.svg.get( name )
    if str:
      v, u = parseLengthWithUnits( str )
      if not v:
        raise ValueError ('Couldn\'t parse the value: ' + str)
        return None
      elif ( u == '' ) or ( u == 'px' ) or ( u == 'mm') or (u == 'cm'):
        return v
      elif u == '%':
        return float( default ) * v / 100.0
      else:
        raise ValueError ('Unsupported units: ' + str)
        return None
    else:
      # No width specified; assume the default value
      return float( default )

  def getScaleOfSVG (self):
    str = self.svg.get ('width')
    if (str):
       v, u = parseLengthWithUnits (str);
       if (u == 'mm'):
         return 1.0  
       elif (u == 'cm'):
         return 0.1
    return 0.28222 # 0.28222 scale determined by comparing pixels-per-mm in a default Inkscape file.
    

  def parse(self):
    scale = self.getScaleOfSVG ()  
    self.svgWidth = self.getLength('width', 354) * scale
    self.svgHeight = self.getLength('height', 354) * scale
    self.recursivelyTraverseSvg(self.svg, [[scale, 0.0, 0.0], [0.0, -scale, self.svgHeight]]) # mirror on X axis, offset paralell to Y

  # TODO: center this thing
  def recursivelyTraverseSvg(self, nodeList, 
                             matCurrent = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0]],
                             parent_visibility = 'visible'):
    """
    Recursively traverse the svg file to plot out all of the
    paths.  The function keeps track of the composite transformation
    that should be applied to each path.

    This function handles path, group, line, rect, polyline, polygon,
    circle, ellipse and use (clone) elements. Notable elements not
    handled include text.  Unhandled elements should be converted to
    paths in Inkscape.

    TODO: There's a lot of inlined code in the eggbot version of this
    that would benefit from the Entities method of dealing with things.
    """
    for node in nodeList:
      # Ignore invisible nodes
      v = node.get('visibility', parent_visibility)
      if v == 'inherit':
        v = parent_visibility
      if v == 'hidden' or v == 'collapse':
        pass

      # first apply the current matrix transform to this node's transform
      matNew = inkex.Transform(matCurrent) * inkex.Transform(node.get("transform")).matrix


      if node.tag == inkex.addNS('g','svg') or node.tag == 'g':
        if (node.get(inkex.addNS('groupmode','inkscape')) == 'layer'):
          layer_name = node.get(inkex.addNS('label','inkscape'))
        self.recursivelyTraverseSvg(node, matNew, parent_visibility = v)
      elif node.tag == inkex.addNS('use','svg') or node.tag == 'use':
        refid = node.get(inkex.addNS('href','xlink'))
        if refid:
          # [1:] to ignore leading '#' in reference
          path = '//*[@id="%s"]' % refid[1:]
          refnode = node.xpath( path )
          if refnode:
            x = float(node.get('x','0'))
            y = float(node.get('y','0'))
            # Note: the transform has already been applied
            if (x!=0) or (y!=0):
              matNew2 = composeTransform(matNew,parseTransform('translate(%f,%f)' % (x,y)))
            else:
              matNew2 = matNew
            v = node.get('visibility',v)
            self.recursivelyTraverseSvg(refnode,matNew2,parent_visibility=v)
          else:
            pass
        else:
          pass
      elif not isinstance(node.tag, str):
        pass
      else:
        entity = self.make_entity(node, matNew)
        if entity == None:
          if (hasattr (node, 'tag_name')):
            inkex.errormsg('Warning: unable to draw object \"' + node.tag_name + '", please convert it to a path first.')
          else:
            inkex.errormsg('Warning: unable to draw object, please convert it to a path first.')

  def make_entity(self,node,mat):
    for nodetype in SvgParser.entity_map.keys():
      tag = nodetype
      ns = 'svg'
      if(type(tag) is tuple):
        tag = nodetype[0]
        ns = nodetype[1]
      if node.tag == inkex.addNS(tag,ns) or node.tag == tag:
        constructor = SvgParser.entity_map[nodetype]
        entity = constructor()
        entity.load(node,mat)
        self.entities.append(entity)
        return entity
    return None
