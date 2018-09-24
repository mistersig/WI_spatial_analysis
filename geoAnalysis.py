import tkinter #GUI 
import matplotlib as mlt
import geopandas as gpd 
import pandas as pd
import gdal
import numpy as np 
from osgeo import ogr #Read shapefile 
import os 


#######################################################################################
#######################################################################################
#######################################################################################

# wPath = '/Users/Sigfrido/Documents/project1/geospatialProject1/data/files/well_nitrate/'
wPath = os.path.abspath('data/files/well_nitrate')
# print(wPath)
wFile = '/well_nitrate.shp'
#well shape 
wellNitrate = wPath + wFile
print(wellNitrate)

#currently has both cancer and NITRATE AGGS
cPath = os.path.abspath('data/files/cancer_tracts')
cFile ='/cancer_tracts.shp'
#cancer Shape
cancerTract = cPath + cFile

#outPut
oPath =os.path.abspath('data/outFiles')
oTiff = '/test.tiff'
#rasterOutput IDW
wIDWresult = oPath + oTiff
#Raster2Polygon
rPolyShape= '/wellsPolygon.shp'
#raster2CSV
cPolyShape= '/wellsPoint.csv'
#csv2pointsShape
pPolyShape= '/wellsPoints.shp'
#Polygon Results 
pResults = oPath + rPolyShape
#CSVresults
cResults = oPath + cPolyShape
#csv2Points 
shpPntResults = oPath + pPolyShape


linearOutput = 'Linear.shp'

lRegression = oPath + linearOutput
#######################################################################################
#######################################################################################
#######################################################################################


file = ogr.Open(wellNitrate)
# print(file)
shape = file.GetLayer(0)
#first feature of the shapefile
feature = shape.GetFeature(0)
#print(feature)
first = feature.ExportToJson()
print(first) # (GeoJSON format)
#{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [25.0, 10.0], [50.0, 50.0]]}, "type": "Feature", "properties": {"FID": 0.0}, "id": 0}


#######################################################################################
#######################################################################################
#######################################################################################
#1 Nitrate levels should use Spatial Interpolation Inverse Weighted Method (IDW) 



# option = gdal.GridOptions(#ot='Float64',
# 	                  format='GTiff',
#                       width=1000,height=1000,
#                       algorithm='invdist',
#                       layers=[wellNitrate],
#                       zfield='nitr_ran'
#                       )

#this methods words to create a gtiff with values I need 
option = gdal.GridOptions(
	                  format='GTiff',
                      # width=1000,height=1000,
                      algorithm='invdist',
                      #outputSRS='EPSG:4326',
                      # layers=[wellNitrate],
                      zfield='nitr_ran'
                      )

out = gdal.Grid(wIDWresult, #results
                    wellNitrate, #shapefile
                    options=option) #options

# out.FlushCache()
out = None
del out

#######################################################################################
#######################################################################################
#######################################################################################


#convert to a CSV
os.system("gdal_translate -of xyz -co ADD_HEADER_LINE=YES -co COLUMN_SEPARATOR=',' {0} {1}".format(wIDWresult,cResults))


#convert from CSV to shapefile
import csv
from shapely.geometry import Point, mapping
from fiona import collection

schema = { 'geometry': 'Point', 'properties': { 'Z': 'float' } }
with collection( shpPntResults, "w", "ESRI Shapefile", schema) as output:
    with open(cResults, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            point = Point(float(row['X']), float(row['Y']))
            output.write({
                'properties': {
                    'Z': row['Z']
                },
                'geometry': mapping(point)
            })

#######################################################################################
#######################################################################################
#######################################################################################

#2  Aggregated Points(well data ) to census tract information 
#Katherine Lechelt

cancerFile = gpd.read_file(cancerTract)

wellPointsShape = gpd.read_file(shpPntResults)
#print(wellPointsShape.head())`

cancerFile.crs = wellPointsShape.crs

wellPointsShape= wellPointsShape.rename(columns={'Z': 'NewNitrate'})


#print(wellPointsShape.head())


# join = gpd.sjoin(wellPointsShape,cancerFile, how="inner", op="contains")

# join = gpd.sjoin(cancerFile, wellPointsShape, how="inner", op="within")
#original
# join = gpd.sjoin( wellPointsShape, cancerFile, how="inner", op="contains")




join = gpd.sjoin(cancerFile, wellPointsShape, how="left")
print(join.head())

# import geopandas
# from geopandas.tools import sjoin
# point = geopandas.GeoDataFrame.from_file('point.shp') # or geojson etc
# poly = geopandas.GeoDataFrame.from_file('poly.shp')
# pointInPolys = sjoin(point, poly, how='left')
# pointSumByPoly = pointInPolys.groupby('PolyGroupByField')['fields', 'in', 'grouped', 'output'].agg(['sum'])


# Output path
#outfp = lRegression

# Save to disk
join.to_file(lRegression)
print('DONE!!!!!!!!!!!!')

#######################################################################################
#######################################################################################
#######################################################################################

#3 Once aggregated, SPATIAL REGRESSION to find the relationship.

#######################################################################################
#######################################################################################
#######################################################################################

#4 USE tkinter to build a GUI

'''

Resources 
https://macwright.org/2012/10/31/gis-with-python-shapely-fiona.html








'''


