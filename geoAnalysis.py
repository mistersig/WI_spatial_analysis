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

wPath = '/Users/sig/projects/geospatialProject1/data/files/well_nitrate/'
wFile = 'well_nitrate.shp'
#well shape 
wellNitrate = wPath + wFile


#currently has both cancer and NITRATE AGGS
cPath = '/Users/sig/projects/geospatialProject1/data/files/cancer_tracts/'
cFile ='cancer_tracts.shp'
#cancer Shape
cancerTract = cPath + cFile

#outPut
oPath ='/Users/sig/projects/geospatialProject1/data/outFiles/'
oTiff = 'test.tiff'
#rasterOutput IDW
wIDWresult = oPath + oTiff
#Raster2Polygon
rPolyShape= 'wellsPolygon.shp'
#raster2CSV
cPolyShape= 'wellsPoint.csv'
#csv2pointsShape
pPolyShape= 'wellsPoints.shp'
#Polygon Results 
pResults = oPath + rPolyShape
#CSVresults
cResults = oPath + cPolyShape
#csv2Points 
shpPntResults = oPath + pPolyShape
#######################################################################################
#######################################################################################
#######################################################################################


file = ogr.Open(wellNitrate)
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

out.FlushCache()
out = None
del out

#######################################################################################
#######################################################################################
#######################################################################################
#1.b convert the Tiff into a shapefile

# srcRaster = gdal.Open(wIDWresult)
# srcband=srcRaster.GetRasterBand(1)

# drv = ogr.GetDriverByName("ESRI Shapefile")
# dst_ds = drv.CreateDataSource(pResults)
# dst_layer = dst_ds.CreateLayer(pResults, srs = None)

# newField = ogr.FieldDefn('NitrateLevels', ogr.OFTInteger)
# dst_layer.CreateField(newField)

# polygon = gdal.Polygonize(srcband,None, dst_layer, 0, [], callback=None)

# # polygon.FlushCache()
# polygon = None
# del polygon

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
#print(wellPointsShape.head())

cancerFile.crs = wellPointsShape.crs

wellPointsShape= wellPointsShape.rename(columns={'Z': 'NewNitrate'})


#print(wellPointsShape.head())


join = gpd.sjoin(wellPointsShape,cancerFile, how="inner", op="within")


print(join.head())




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


