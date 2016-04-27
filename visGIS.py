'''
 GIS conversion/interpolation tools for use in VisIt
 (http://wci.llnl.gov/codes/visit/).
 Relies on ogr/gdal.
'''
__author__ = 'fluidmotion'

import os,sys
from osgeo import ogr, gdal
import numpy as np
import matplotlib.pyplot as plt

class shpTools():
    '''
    accepts line shapefile of contours - interpolates
    to an ascii grid using scipy.
    example data from
    http://www.swfwmd.state.fl.us/data/gis/layer_library/category/potmaps
    '''

    def __init__(self, shp, outfile, fld, cellsize, interptype='rbf', wkt=''):
        self.shp = shp
        self.fld = fld
        self.outfile = outfile
        self.cellsize = cellsize
        self.nrow = 0
        self.ncol = 0
        self.x = 0
        self.y = 0
        self.z = []
        self.ext = 0
        self.interptype = interptype
        self.wkt = wkt
        self.minval = -1e30
        
    def getVerts(self):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        ds = driver.Open(self.shp)
        lyr = ds.GetLayer(0)
        self.ext = lyr.GetExtent()
        self.nrow = int((self.ext[3]-self.ext[2])/self.cellsize)
        self.ncol = int((self.ext[1]-self.ext[0])/self.cellsize)
        x = []
        y = []
        print 'getting vertices...'
        for i in range(len(lyr)):
            pts = lyr.GetNextFeature()
            geom = pts.GetGeometryRef().Clone()
            v = geom.GetPoints()
            for verts in v:
                x.append(verts[0])
                y.append(verts[1])
                self.z.append(pts.GetFieldAsDouble(self.fld))
        self.x = np.array(x)
        self.y = np.array(y)

        print(self.nrow, self.ncol)
 
    def grid2dem(self):

        hdr = 'ncols         {}\n'.format(self.ncol)
        hdr = hdr+'nrows         {}\n'.format(self.nrow)
        hdr = hdr+'xllcorner     {}\n'.format(self.ext[0])
        hdr = hdr+'yllcorner     {}\n'.format(self.ext[2])
        hdr = hdr+'cellsize      {}\n'.format(self.cellsize)
        hdr = hdr+'NODATA_value  -999'
        np.savetxt(self.outfile,np.flipud(self.grid.T), header=hdr, comments='')

    def checkdups(self, source):
        # http://stackoverflow.com/questions/5419204/index-of-duplicates-items-in-a-python-list
        from collections import defaultdict

        def list_duplicates(seq):
            tally = defaultdict(list)
            for i,item in enumerate(seq):
                tally[item].append(i)
            # return ((key,locs) for key,locs in tally.items() 
                                    # if len(locs)>1)
            return (locs for key,locs in tally.items() 
                                    if len(locs)>1)

        # for dup in sorted(list_duplicates(source)):
        return sorted(list_duplicates(source))
            # print dup


    def interpGrid(self):
        ptx = np.array(self.x)
        pty = np.array(self.y)
        z = np.array(self.z)
        print(len(ptx), 'length x')
        # remove duplicate x values
        dups = self.checkdups(self.x)
        ptx = np.delete(ptx, dups)
        pty = np.delete(pty, dups)
        z = np.delete(z, dups)
        print(len(ptx), 'length x')

        pts = zip(self.x, self.y)
        # gridx, gridy = np.mgrid[uprLeft[0]:lwrRight[0]:50j,uprLeft[1]:lwrRight[1]:50j]
        gridx, gridy = np.mgrid[self.ext[0]:self.ext[1]:self.ncol*1j,
                            self.ext[2]:self.ext[3]:self.nrow*1j]
        ##### using griddata #####
        if self.interptype == 'griddata':
            from scipy.interpolate import griddata
            self.grid = griddata(pts,self.z,(gridx,gridy), method='cubic',fill_value=-3e30)
        #### examples from 
        ##### http://stackoverflow.com/questions/24978052/interpolation-over-regular-grid-in-python
        ##### using radial basis function ####
        if self.interptype == 'rbf':
            import scipy.interpolate as interpolate
            f = interpolate.Rbf(pty, ptx, z, function='linear')
            self.grid = f(gridy, gridx)

        ##### using kriging ####
        if self.interptype == 'gauss':
            from sklearn.gaussian_process import GaussianProcess
            # print math.sqrt(np.var(z))
            # gp = GaussianProcess(theta0=0.1, thetaL=1.1, thetaU=10.1, nugget=0.000001)
            if np.min(z) <= 0:
                thetaL = 0.1
            else:
                thetaL = np.min(z)

            print(np.min(z), thetaL, np.max(z))
            # gp = GaussianProcess(regr='quadratic',corr='cubic',theta0=np.min(z),thetaL=thetaL,thetaU=np.max(z),nugget=0.05)
            gp = GaussianProcess(theta0=500,thetaL=100,thetaU=2000)
            gp.fit(X=np.column_stack([pty,ptx]),y=z)
            rr_cc_as_cols = np.column_stack([gridy.flatten(), gridx.flatten()])
            self.grid = gp.predict(rr_cc_as_cols).reshape((self.ncol,self.nrow))

        if self.interptype == 'krig':
            import pyKriging  
            from pyKriging.krige import kriging  
            from pyKriging.samplingplan import samplingplan
            
            # The Kriging model starts by defining a sampling plan, we use an optimal Latin Hypercube here
            # sp = samplingplan(2)  
            # X = sp.optimallhc(20)
            # print(X)
            X = np.array(zip(self.x, self.y))
            print(X.shape)
            
            # Next, we define the problem we would like to solve
            testfun = pyKriging.testfunctions().squared  
            # y = testfun(X)
            # print(y)
            y = self.z
            
            # Now that we have our initial data, we can create an instance of a Kriging model
            k = kriging(X, y)#, testfunction=testfun, name='simple')  
            # k.train()
            
            # Now, five infill points are added. Note that the model is re-trained after each point is added
            # numiter = 5  
            # for i in range(numiter):  
                # print 'Infill iteration {0} of {1}....'.format(i + 1, numiter)
                # newpoints = k.infill(1)
                # for point in newpoints:
                    # k.addPoint(point, testfun(point)[0])
                # k.train()
            
            # And plot the results
            k.plot() 
            sys.exit()

        self.grid[self.grid < self.minval] = -2.99999989403e+030 #self.minval
        self.grid = np.flipud(self.grid.T)

    @staticmethod
    def getExtent(gt,cols,rows):
        ''' Return list of corner coordinates from a geotransform
    
            @type gt:   C{tuple/list}
            @param gt: geotransform
            @type cols:   C{int}
            @param cols: number of columns in the dataset
            @type rows:   C{int}
            @param rows: number of rows in the dataset
            @rtype:    C{[float,...,float]}
            @return:   coordinates of each corner
        '''
        ext=[]
        xarr=[0,cols]
        yarr=[0,rows]
    
        # for px in xarr:
            # for py in yarr:
        minx = gt[0] + (0 * gt[1]) + (0 * gt[2])
        miny = gt[3] + (0 * gt[4]) + (rows * gt[5])
        maxx = gt[0] + (cols * gt[1]) + (rows * gt[2])
        maxy = gt[3] + (cols * gt[4]) + (0 * gt[5])
        ext = [minx, maxx, miny, maxy]
        print minx,maxx, miny, maxy
            # yarr.reverse()
        return ext

    def writeRaster(self):

        print 'writing tiff...'
        xres = (self.ext[1] - self.ext[0]) / float(self.ncol)
        yres = (self.ext[3] - self.ext[2]) / float(self.nrow)
        geotransform = (self.ext[0], xres, 0, self.ext[3], 0, -yres)   
        drv = gdal.GetDriverByName('GTiff')
        ds = drv.Create(self.outfile, self.ncol, self.nrow, 1 ,gdal.GDT_Float32)  # Open the file
        band = ds.GetRasterBand(1)
        band.SetNoDataValue(-3e30)
        ds.SetGeoTransform(geotransform)  # Specify its coordinates

        if self.wkt != '':
            ds.SetProjection(self.wkt)   # Exports the coordinate system 
        band.WriteArray(self.grid)   # Writes my array to the raster
        # band.WriteArray(np.flipud(self.grid.T))   # Writes my array to the raster
        #http://gis.stackexchange.com/questions/37238/writing-numpy-array-to-raster-file
        # print grid.shape
