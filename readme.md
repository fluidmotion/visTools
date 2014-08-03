# VisMod

While the ultimate goal of VisMod is to assist in groundwater flow model visualization,
the current classes support the export of files that can be used in visualization software
such as [http://wci.llnl.gov/codes/visit/].

[![Animation created with VisIt from MODFLOW results](http://i.ytimg.com/vi/v12i04psF2c/mqdefault.jpg)]
(http://www.youtube.com/watch?v=v12i04psF2c)

## Dependencies

VisMod expects binary head output from modflow [http://water.usgs.gov/ogw/modflow/],
and writes BOV (Brick of Values) files for visualization in VisIt 
[https://wci.llnl.gov/codes/visit/]
 
Currently VisMod supports only uniform grid models (x and y dimensions can differ,
 but they cannot be variably spaced).
 
## Input requirements

1. Model layer to be exported for visualization
2. Model precision (single or double)
3. Model cell dimensions in the x and y directions
4. Origin of bottom left of the model grid (if unknown, any values will work)
5. Path and name of binary head output file from MODFLOW
6. Output path for BOV files

## Outputs

1. BOV file for each timestep or stress period specifed as
'SAVE HEAD' in the MODFLOW OC (output control) file.
2. .visit file for use in VisIt, which contains the name of each BOV
file produced by VisMod - useful for time series animations

## Workflow

1. Ensure that visMod.py and runVisMod.py exist in the same directory
2. Modify user variables in runVisMod.py
3. Ensure output path exists

Example call to class to format MODFLOW heads for VisIt--
```
origin=[0.0,0.0]  #origin of bottom left corner
xdim=2000 #cell dimension in the x direction
ydim=1000 #cell dimension in the y direction
layer=1 #layer to be exported
precision='single' #single or double
headsfile='MF2005.1_11/test-run/tr2k_s3.hed'
outpath='MF2005.1_11/MF2005.1_11/test-run/visit/'

v=vm.visMod(layer,precision,xdim,ydim,origin,headsfile,outpath)
v.BOVheads()
```

#visGIS

visGIS utility tools to visualize GIS files in visualization.
Currently one class is included to convert a shapefile of contours
into a continous grid in ASCII DEM format.

## Dependencies

VisGIS expects a line shapefile with an attribute of values (normally to represent
altitude of water table or land surface)
and writes a .dem file (ASCII DEM format) files for visualization in VisIt
[https://wci.llnl.gov/codes/visit/]
VisGIS has been tested with python (x,y) with GDAL installed.
required modules are osgeo, numpy, and scipy
  
## Input requirements

1. Line shapefile with attribute of elevations
2. Output grid cell size
3. Path and name of dem output file

## Outputs

1. ASCII DEM file

## Workflow
Example data from
[http://www.swfwmd.state.fl.us/data/gis/layer_library/category/potmaps]
    
Example call to class to interpolate shapefile of contours
```
import visGIS as vg
c2g=vg.shpTools('may75fl_line.shp',
                'may75fl.dem','M75FLEL',500)
c2g.getVerts() #required for interp2dem
c2g.interp2dem()
```