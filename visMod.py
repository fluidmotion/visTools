'''
 utilities for groundwater flow model visualization
 expects binary head output from modflow (http://water.usgs.gov/ogw/modflow/)
 writes BOV files for visualization in VisIt (https://wci.llnl.gov/codes/visit/)
 
 currently supports only uniform grid models (x and y dimensions can differ,
 but they cannot be variably spaced)
'''
__author__='fluidmotion'

import os,sys,struct

class visMod():
    '''class to read modflow binary heads and write bov files for VisIt
    expects model layer to be visualized, model precision, x and y cell dimensions
    origin of bottom left, name of binary heads file, output path for BOV
    '''
    def __init__(self,layer,precision,xdim,ydim,origin,filename,outpath):
        self.layer=layer
        self.precision=precision.lower()
        self.xdim=xdim
        self.ydim=ydim
        self.origin=origin
        self.filename=filename
        self.outpath=outpath
        self.fvis=''
        self.nPer=0
        self.nStep=0
        self.outrel=''
        self.relhdsfile=''
        self.col=0
        self.row=0
        self.iLay=0
        self.bytepos=0
        self.type='hds'
        self.fobj=''
  
    def BOVheads(self):
        prec=4
        if self.precision=='double':
            prec=8  
        if not os.path.exists(self.outpath):
            print('{} does not exist or cannot be found'.format(self.outpath))
            exit()
        self.outrel=os.path.relpath(self.outpath)
        curdir=os.getcwd()
        os.chdir(self.outrel)
        if not os.path.exists(self.filename):
            print('{} does not exist or cannot be found'.format(self.filename))
            exit()
        self.relhdsfile=os.path.relpath(self.filename)
        os.chdir(curdir)
        f=open(self.filename,'rb')
          
        for i in range(0,self.layer):
            bytepos=0
            f.seek(0,2)
            fileend=f.tell()
            f.seek(0)
            self.fvis=open(os.path.join(self.outrel,'bovlayer'+str(self.layer)+'.visit'),'w')
            while self.bytepos<=fileend:
                self.readheader(f)
                self.bytepos=f.tell()
                if self.iLay==self.layer:
                    self.writeBOV()
                self.bytepos=self.row*self.col*prec+f.tell()
                f.seek(self.bytepos)
                if self.bytepos>=fileend:
                    break
            self.fvis.close()
        f.close()
  
    def readheader(self,f):
        self.nStep = struct.unpack('i',f.read(4))[0]
        self.nPer = struct.unpack('i',f.read(4))[0]
        if self.precision=='single':
            perLen = struct.unpack('f',f.read(4))
            StartTime = struct.unpack('f',f.read(4))
        else:
            perLen = struct.unpack('d',f.read(8))
            StartTime = struct.unpack('d',f.read(8))    
        textType = f.read(16)
        self.col = struct.unpack('i',f.read(4))[0]
        self.row = struct.unpack('i',f.read(4))[0]
        self.iLay = struct.unpack('i',f.read(4))[0]

    def writeBOV(self):
        print 'BOV '+self.type+' layer='+str(self.layer)+' stress period='+str(self.nPer)+' time step='+str(self.nStep)
        outfile=open(os.path.join(self.outrel,self.type+'SP'+str(self.nPer)+'TS'+str(self.nStep)+'Lay'+str(self.layer)+'.bov'),'w')
        self.fvis.write(self.type+'SP'+str(self.nPer)+'TS'+str(self.nStep)+'Lay'+str(self.layer)+'.bov\n')
        outfile.write('TIME: '+str(self.nPer)+'.'+str(self.nStep)+'\n')
        outfile.write('DATA_FILE: '+self.relhdsfile+'\n')
        outfile.write('DATA SIZE: '+str(self.col)+' '+str(self.row)+' 1\n')
        if self.precision=='double':
            outfile.write('DATA_FORMAT: DOUBLE\n')
        else:
            outfile.write('DATA_FORMAT: FLOAT\n')
        outfile.write('VARIABLE: simHeads\n')
        outfile.write('DATA_ENDIAN: LITTLE\n')
        outfile.write('CENTERING: zonal\n')
        outfile.write('BRICK ORIGIN: '+str(self.origin[0])+' '+str(self.origin[1])+' 0.\n')
        outfile.write('BRICK_SIZE: '+str(self.col*self.xdim)+' '+str(self.row*self.ydim)+' 1.\n')
        outfile.write('BYTE_OFFSET: '+str(self.bytepos)+'\n')
        outfile.close()
        