import cherrypy
import math

try:
    import mapnik2 as mapnik
except ImportError:
    import mapnik

class SphericalMercator(object):
  """
  Python class defining Spherical Mercator Projection.

  Originally from:
    http://svn.openstreetmap.org/applications/rendering/mapnik/generate_tiles.py
  """
  def __init__(self,levels=18,size=256):
    self.Bc = []
    self.Cc = []
    self.zc = []
    self.Ac = []
    self.levels = levels
    self.DEG_TO_RAD = math.pi/180
    self.RAD_TO_DEG = 180/math.pi
    self.size = size

    for d in range(0,levels):
      e = size/2.0;
      self.Bc.append(size/360.0)
      self.Cc.append(size/(2.0 * math.pi))
      self.zc.append((e,e))
      self.Ac.append(size)
      size *= 2.0

  @classmethod
  def minmax(data):
    a = max(a,b)
    a = min(a,c)
    return a

  @classmethod
  def is_merc(srs):
    srs = srs.lower()
    if 'epsg:900913' in srs:
      return True
    elif 'epsg:3857' in srs:
      return True
    elif not 'merc' in srs:
      return False
    # strip optional modifiers (those without =)
    # TODO: find a better way of doing this. Legacy
    elements = dict([p.split('=') for p in srs.split() if '=' in p])

    for p in elements:
      if MERC_ELEMENTS.get(p, None) != elements.get(p, None):
        return False
    return True

  def espg_4326_to_pixel(self, px, zoom):
    # TODO: rename arguments from single character names to something meaningful
    d = self.zc[zoom]
    e = round(d[0] + px[0] * self.Bc[zoom])
    f = self.minmax(math.sin(DEG_TO_RAD * px[1]),-0.9999,0.9999)
    g = round(d[1] + 0.5 * math.log((1+f)/(1-f))*-self.Cc[zoom])
    return (e, g)

  def pixel_to_espg_4326(self, px, zoom):
    """ Convert pixel postion to LatLong (EPSG:4326) """
    # TODO - more graceful handling of indexing error
    e = self.zc[zoom]
    f = (px[0] - e[0])/self.Bc[zoom]
    g = (px[1] - e[1])/-self.Cc[zoom]
    h = self.RAD_TO_DEG * ( 2 * math.atan(math.exp(g)) - 0.5 * math.pi)
    return (f, h)

  def xyz_to_envelope(self,x,y,zoom, tms_style=False):
    """ Convert XYZ to mapnik.Envelope """
    # flip y to match TMS spec
    if tms_style:
        y = (2**zoom-1) - y
    ll = (x * self.size,(y + 1) * self.size)
    ur = ((x + 1) * self.size, y * self.size)
    minx,miny = self.pixel_to_espg_4326(ll, zoom)
    maxx,maxy = self.pixel_to_espg_4326(ur, zoom)
    lonlat_bbox = mapnik.Envelope(minx,miny,maxx,maxy)
    env = mercator.forward(lonlat_bbox)
    return env

MERC_PROJ4 =  '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 ' \
              '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over'

class Server():
  def __init__(self, path_to_mapfile):
    self.max_zoom   = 22
    self.image_size = 256
    self.mapnik     = mapnik.Map(self.image_size, self.image_size)
    self.mapnik.srs = MERC_PROJ4
    self.mercator   = SphericalMercator(levels=self.max_zoom+1,size=self.image_size)

    mapnik.load_map(self.mapnik, path_to_mapfile)
    if not is_merc(self.mapnik.srs):
      self.mapnik_map.srs = MERC_PROJ4
      # NOTE: Add better logging
      print 'Forcing Merc Projection.'

    self.mapnik_map.zoom_all()
    self.envelope = self._mapnik_map.envelope()

  @cherrypy.expose
  def index(self):
    x   = cherrypy.request.headers['x']
    y   = cherrypy.request.headers['y']
    z   = cherrypy.request.headers['z']
    img = mapnik.Image()
    img.background = self._mapnik_map.background

    if not x or not y or not z:
      error_msg = "Failed request:\n\tx: %s\n\ty: %s\n\tz: %s\n" % (x, y, z)
      cherrypy.reponse.headers["Status"] = "400"
      return error_msg
    else:
      # NOTE: Process request correctly
      x         = int(x)
      y         = int(y)
      z         = int(z)
      envelope  = self.merc.xyz_to_envelope(x,y,zoom)

      if self.envelope.intersects(envelope):
        self._mapnik_map.zoom_to_box(envelope)
        self._mapnik_map.buffer_size = self.buffer_size
        mapnik.render(self._mapnik_map, img)
        cherrypy.reponse.headers["Status"] = "200"

    return img.tostring('png256')

  @classmethod
  def parse_config(cfg_file):
    from ConfigParser import SafeConfigParser
    config = SafeConfigParser()
    config.read(cfg_file)
    params = {}
    for section in config.sections():
      options = config.items(section)
      for param in options:
        params[param[0]] = param[1]
    return params

if __name__ == '__main__':
  # NOTE: change path to something more universal
  root = Server('/home/bordicon/workspace/personal/mapnik-style/osm.xml')
  cherrypy.quickstart(root)
