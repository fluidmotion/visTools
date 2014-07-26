'''
 GIS conversion/interpolation tools for use in VisIt
 (http://wci.llnl.gov/codes/visit/).
 Relies on ogr/gdal.
'''
__author__='fluidmotion'

import os,sys
from osgeo import ogr,gdal
import numpy as np
from scipy.interpolate import griddata

class shpTools():
    '''accepts line shapefile of contours - interpolates
    to an ascii grid using scipy.
    example from
    http://www.swfwmd.state.fl.us/data/gis/layer_library/category/potmaps'''
    def __init__(self,shp,outfile,fld,cellsize):
        self.shp=shp
        self.fld=fld
        self.outfile=outfile
        self.cellsize=cellsize
        self.rows=0
        self.cols=0
        self.x=0
        self.y=0
        self.z=[]
        self.ext=0
        
    def getVerts(self):
        driver=ogr.GetDriverByName('ESRI Shapefile')
        ds=driver.Open(self.shp)
        lyr=ds.GetLayer(0)
        self.ext=lyr.GetExtent()
        self.rows=int((self.ext[3]-self.ext[2])/self.cellsize)
        self.cols=int((self.ext[1]-self.ext[0])/self.cellsize)
        x=[]
        y=[]
        print 'getting vertices...'
        for i in range(len(lyr)):
            pts=lyr.GetNextFeature()
            geom=pts.GetGeometryRef().Clone()
            v=geom.GetPoints()
            for verts in v:
                x.append(verts[0])
                y.append(verts[1])
                self.z.append(pts.GetFieldAsDouble(self.fld))
        self.x=np.array(x)
        self.y=np.array(y)
 
    def interp2dem(self):
        gx,gy=np.mgrid[int(min(self.x)):int(max(self.x)):complex(self.cols),
                       int(min(self.y)):int(max(self.y)):complex(self.rows)]
        print 'interpolating...'
        interp=griddata((self.x,self.y),self.z,(gx,gy),fill_value=-9999)
        hdr='ncols         {}\n'.format(self.cols)
        hdr=hdr+'nrows         {}\n'.format(self.rows)
        hdr=hdr+'xllcorner     {}\n'.format(self.ext[0])
        hdr=hdr+'yllcorner     {}\n'.format(self.ext[2])
        hdr=hdr+'cellsize      {}\n'.format(self.cellsize)
        hdr=hdr+'NODATA_value  -999'
        np.savetxt(self.outfile,np.flipud(interp.T),header=hdr,comments='')
