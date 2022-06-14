import ee#, eemont
ee.Authenticate()
ee.Initialize()

#%%

import geemap
from importlib import reload
import geopandas as gpd

#%%

from modules import high_level_functions
from modules import utils_Landsat_SR as utils_LS
from modules import ms_indices as indices
from modules import configs, utils_string

#%%

utils_string = reload(utils_string)

#%%

# PROPERTIES
# SET METADATA PARAMETERS
MAXCLOUD = 70
STARTYEAR = 2001
ENDYEAR = 2020
STARTMONTH = 7
ENDMONTH = 8
SCALE = 30
longitudes = [-140]
latitudes = [65]
SIZE_LON = 0.1
SIZE_LAT = 0.1

# target_collection = 'users/ingmarnitze/TCTrend_SR_2001-2020_TCVIS'
# target_collection_nObs = 'users/ingmarnitze/TCTrend_SR_2001-2020_nObservations'

# %%

# image metadata Filters
config_trend = {
 'date_filter_yr': ee.Filter.calendarRange(STARTYEAR, ENDYEAR, 'year'),
 'date_filter_mth': ee.Filter.calendarRange(STARTMONTH, ENDMONTH, 'month'),
 'meta_filter_cld': ee.Filter.lt('CLOUD_COVER', MAXCLOUD),
 'select_bands_visible': ["B1", "B2", "B3", "B4"],
 'select_indices': ["TCB", "TCG", "TCW", "NDVI", "NDMI", "NDWI"],
 'select_TCtrend_bands': ["TCB_slope", "TCG_slope", "TCW_slope"],
 'geom': None
}
# ------ RUN FULL PROCESS FOR ALL REGIONS IN LOOP ------------------------------
# Map.addLayer(imageCollection, {}, 'TCVIS')

# %%

RUN = 0

# %%

Map = geemap.Map()
Map.add_basemap(basemap='SATELLITE')

# %%

for lowLat in latitudes:
 for leftLon in longitudes:

  # check for Hemisphere
  if lowLat < 0:
   sizeLat = SIZE_LAT * -1
  else:
   sizeLat = SIZE_LAT

  sizeLon = SIZE_LON

  # create Bounding Box
  geom = ee.Geometry.Polygon(
   [leftLon, lowLat + sizeLat, leftLon, lowLat, leftLon + sizeLon, lowLat, leftLon + sizeLon, lowLat + sizeLat])
  config_trend['geom'] = geom
  Map.addLayer(geom, {}, str(lowLat))

  trend = high_level_functions.runTCTrend(config_trend)

# %%

config_trend['select_bands_visible']

# %%

RUN = 1

# %%

for index in config_trend['select_indices']:
 data = trend['data'].select(f'{index}.*')
 if RUN:
  task = ee.batch.Export.image.toDrive(
   image=data.multiply(1e-4),
   description=f'image_{index}',
   folder='PDG_Trend',
   fileNamePrefix=f'image_{index}',
   region=geom,
   scale=30,
   maxPixels=1e12)
  task.start()

# %%

Map.center_object(geom)
Map

# %%


