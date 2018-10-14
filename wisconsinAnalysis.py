from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")
import matplotlib as mlt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf
import statsmodels.formula.api as sm
from matplotlib.figure import Figure
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import geopandas as gpd
from osgeo import ogr #Read shapefile 
import pandas as pd
import numpy as np 
import gdal
import sys
import os 
# import folium #who knows if I need it ???


cancerCensus ='/Users/Sigfrido/Documents/project1/geospatialProject1/data/files/cancerTracts/cancerTracts.shp'
nitrateWell = '/Users/Sigfrido/Documents/project1/geospatialProject1/data/files/well_nitrate/well_nitrate.shp'
outputDirectory ='/Users/Sigfrido/Documents/project1/geospatialProject1/data/outFiles/'
realLinear = '/Users/Sigfrido/Documents/project1/geospatialProject1/data/outFiles/realLinear.shp'
# from tkinter import ttk

class GuiApplication(Frame):
	'''
	This class is the GUI and holds the entire application
	'''
	def __init__ (self):

		Frame.__init__(self)
		#master is the reference to the master widget 
		# self.master = master 
		#window 
		self.init_window()

	def init_window(self):
		#title
		self.master.title("Wisconsin Cancer Spatial Assesment")
		#geometry w x h
		self.master.geometry('800x1000')
		#display initial map 
		self.display_map()
		#display the test for the intial start up
		self.display_text()


	def display_text(self):
		self.text2 = Text(self.master, height=5, width=70)
		self.text2.tag_configure('stuff',font=('Tempus Sans ITC', 12, 'bold'))
		self.quote = """            Is there a relationship between nitrate levels and cancer rates? \nExplore the relationship between nitrate levels in water wells, and cancer in the \nstate of Wisconsin. Use the tools below to create a map for \nOrdinary least squares (OLS). """
		self.text2.insert(END, self.quote, 'stuff')
		self.text2.grid(column=1, row=2)

		self.enterValue =Label(self.master, text="Enter a value for IDW Analysis")
		self.enterValue.grid(column=1, row=3)

		# VARIABLE INPUT		
		self.pathIDW = Entry(self.master,width=10)
		self.pathIDW.grid(column=1, row=4)
		# self.pathIDW.insert(0)
		#RUN ANALYSIS BUTTON
		Button(self.master, text="Run Analysis", command=self.getInput).grid(column=1, row=5)
		#for seeing the results map only works if the analysis as all ready produce a results layer
		Button(self.master, text="Residual Results Button", command=self.results_residual_map).grid(column=1, row=8)#for developer only

	def display_map(self):
		#this is the map 
		self.world = gpd.read_file(cancerCensus)
		self.cities = gpd.read_file(nitrateWell)
		#plots the figures
		self.fig, self.ax = plt.subplots(1, figsize=(8,8))
		# set aspect to equal. This is done automatically
		# when using *geopandas* plot on it's own, but not when
		# working with pyplot directly.
		# self.ax.set_aspect('equal')
		self.ax.set_aspect('equal')
		self.world.plot(ax=self.ax, color='#ccd9ff', edgecolor='white', label='WI Census Tracts')
		# self.world.plot(ax=self.ax, cmap='OrRd', edgecolor='black',column='canrate')
		self.cities.plot(ax=self.ax, marker='*', color='green', markersize=5,label='Well Locations')
		#legend accommodations		
		self.legend_elements = [Line2D([0], [0], marker='o', color='w', label='Nitrate Well Samples',markerfacecolor='g', markersize=5),
		mpatches.Patch(facecolor='#ccd9ff',label='WI Census Tracts')]#edgecolor='r'
		self.ax.legend(handles=self.legend_elements)
		# self.ax.legend([self.cities,self.world],['Well Locations', 'WI counties'])
		self.ax.set_title('Mapping Cancer Rates & Nitrate Levels in Wisconsin', fontsize = 14)
		self.ax.set_xlabel('Longitude', fontsize = 12)
		self.ax.set_ylabel('Latitude', fontsize = 12)

		self.canvas = FigureCanvasTkAgg(self.fig,self)
		self.canvas.draw()
		self.canvas.get_tk_widget().grid()
		self.canvas.draw()
		self.grid(column=1, row=1)

	def results_residual_map(self):
		print("running results residuals map")
		self.resultsWindow = Toplevel(self.master)
		self.resultsWindow.geometry('800x1000')
		self.resultsWindow.wm_title("Residual Results" )
		print("working on building interactiveMap")
		self.app = interactiveMap(self.resultsWindow)

	def getInput(self):
		a = cancerCensus
		b = nitrateWell
		c = outputDirectory
		d = self.pathIDW.get()
		if int(d) < 1:
			sys.exit()

		self.analysisTest(a,b,c,d)

	def analysisTest(self,cancer_file,nitrate_file,out_dir,IDW_value):
		print('Running the IDW Interpolation')
		# wPath = '/Users/Sigfrido/Documents/project1/geospatialProject1/data/files/well_nitrate/'

		#take the file path from the gui and fun the analysis 
		cancerTract = str(cancer_file)
		wellNitrate = str(nitrate_file)
		oPath = str(out_dir)
		IDW = IDW_value
		
		#files created during the analysis 

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

		nitrate_IDW = 'IDW_Results.shp'

		nitrate_IDW_results = oPath + nitrate_IDW
		#######################################################################################
		file = ogr.Open(wellNitrate)
		# print(file)
		shape = file.GetLayer(0)
		#first feature of the shapefile
		feature = shape.GetFeature(0)
		#print(feature)
		first = feature.ExportToJson()

		#######################################################################################
		#1 Nitrate levels should use Spatial Interpolation Inverse Weighted Method (IDW) 

		print('starting the GDAL Interpolation')
		# option = gdal.GridOptions(format='GTiff',algorithm='invdist:power={0}'.format(IDW),outputSRS='EPSG:4326',zfield='nitr_ran')
		option = gdal.GridOptions(format='GTiff',algorithm='invdist:power={0}'.format(IDW),zfield='nitr_ran')

		out = gdal.Grid(wIDWresult, #results
		                    wellNitrate, #shapefile
		                    options=option) #options

		# out.FlushCache()
		out = None
		del out
		#convert to a CSV
		print("converting out to CSV for next step")
		os.system("gdal_translate -of xyz -co ADD_HEADER_LINE=YES -co COLUMN_SEPARATOR=',' {0} {1}".format(wIDWresult,cResults))

		print("converting CSV to Shapefile using FIONA")
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
		#2  Aggregated Points(well data ) to census tract information 

		print("Aggregating Points to Census Tract Shapefile")
		cancerFile = gpd.read_file(cancerTract)
		wellPointsShape = gpd.read_file(shpPntResults)
		#print(wellPointsShape.head())`
		cancerFile.crs = wellPointsShape.crs
		wellPointsShape= wellPointsShape.rename(columns={'Z': 'NewNitrate'})

		print("Using geopandas to join Cancer Census Tracts with Well Points Shapefile")
		join = gpd.sjoin(cancerFile, wellPointsShape, how="left")

		# Save to disk
		join.to_file(nitrate_IDW_results)
		#prints file path
		# print(nitrate_IDW_results)#not needed 
		print("Building The Regression Residuals Results Map")
		self.results_residual_map()
		print("Analysis Complete")



class interactiveMap:
	def __init__ (self,master):
		self.master = master
		self.frame = Frame(self.master)
		self.master.title("Mapping Results")
		#geometry w x h
		self.master.geometry('800x1000')
		#display the results map 
		self.display_residual_results()#column=1,row=1
		#display the text explaining the results
		self.results_text()

	def display_residual_results(self):
		'''
		The residual standard deviation is a statistical term used to describe the 
		standard deviation of points formed around a linear function and is an estimate 
		of the accuracy of the dependent variable being measured.

		'''

		########
		IDW_results_add_residuals ="/Users/Sigfrido/Documents/project1/geospatialProject1/data/outFiles/IDW_Results.shp"
		print("started residuals function")

		gdf = gpd.read_file(IDW_results_add_residuals)
		#drop the nonTypes in the dataframe
		filtered_data = gdf[~np.isnan(gdf["NewNitrate"])]
		df1 = pd.DataFrame(gdf)
		df1 = df1.fillna(0)

		#applys a residual model from two variables 
		regmodel = 'canrate ~ NewNitrate'
		# df1['residual'] = sm.ols(formula='NewNitrate ~ canrate', data=df1).fit().resid
		df1['residual'] = sm.ols(formula='canrate ~ NewNitrate', data=df1).fit().resid


		df = df1
		#drops the index_right
		columns = ['index_righ']
		df.drop(columns, inplace=True, axis=1)
		#applys crs to new shapefile
		crs = {'init': 'epsg:4326'}
		newGeo = gpd.GeoDataFrame(df,crs=crs,)
		#for testing 
		print(' new geodataframe w/residual')
		# print(newGeo.head())#print the head of the new geoPandas

		# realLinear = "/Users/Sigfrido/Documents/project1/geospatialProject1/data/outFiles/realLinear.shp"
		#realLinear declared as a global all ready so file path above not needed
		newGeo.to_file(realLinear)
		print("Finished writing shapefile")
##########

		print("writing map")
		#this is the map 
		self.residual = gpd.read_file(realLinear)
		# self.cities = gpd.read_file(nitrateWell)

		self.fig, self.ax = plt.subplots(1, figsize=(8,8))
		# set aspect to equal. This is done automatically
		# when using *geopandas* plot on it's own, but not when
		# working with pyplot directly.
		# self.ax.set_aspect('equal')

		self.ax.set_aspect('equal')
		# self.residual.plot(ax=self.ax,column='residual',scheme='QUANTILES', k=8, cmap=plt.cm.Blues, legend=True)
		self.residual.plot(ax=self.ax,column='residual',scheme='QUANTILES', k=6, cmap=plt.cm.Reds, legend=True)#plt.cm.RdYlBu
		# self.ax.legend(title="legend")

		# self.ax.legend(loc='lower left')
		self.ax.set_title('OLS Standard Deviation of Residuals Results', fontsize = 14)
		self.ax.set_title('OLS Residual Results', fontsize = 14)
		self.ax.set_xlabel('Longitude', fontsize = 12)
		self.ax.set_ylabel('Latitude', fontsize = 12)
		# plt.show()
		print('working on canvas')
		self.canvas = FigureCanvasTkAgg(self.fig,self.master)
		self.canvas.get_tk_widget().grid(column=1,row=1)
		self.canvas.draw()
		# self.grid(column=1,row=1)
		print("OLS displayed")
	
	def results_text(self):
		self.text2 = Text(self.master, height=10, width=70)
		self.text2.tag_configure('stuff',font=('Tempus Sans ITC', 12, 'bold'))
		self.quote = """
    The ordinary least squares (OLS) gives a way of taking complicated outcomes. 
Instead of plotting a linear graph we have taken the residuals, an observable 
errors from the estimate coefficients.The residuals are estimates of the errors. 
Moving away from 0 in a positive direction we see a stronger correlation between 
Cancer rates and Nitrate levels. In a negative direction we see weaker 
correlation such as Madison and Milwaukee.

		"""
		self.text2.insert(END, self.quote, 'stuff')
		self.text2.grid(column=1, row=2)


def main(argv):
    # My code here
    # mainApp = guiApplication()
    # print(mainApp)

    root = Tk()
    #instance
    app = GuiApplication()
    root.mainloop()

    pass

if __name__ == "__main__":
    main(sys.argv)











