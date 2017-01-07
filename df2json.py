"""
class to create json files with
parent/child hiearchy from a pandas
DataFrame
example use of the json file would
be in a sunburst plot

"""

import os, sys
import pandas as pd
import json

class jsonMaker(object):

    def __init__(self, sql='', df='', jsonfile=''):
        self.conn = ''
        self.servername = ''
        self.dbname = ''
        self.sql = sql
        self.df = df
        self.jsonfile = jsonfile

    def sqlconn(self):
        """
        example method to connect to a SQL server

        uses pandas to read the return query directly
        into a DataFrame

        """

        import pyodbc

        conn = pyodbc.connect("DRIVER=SQL Server; \
                           SERVER={0}; \
                           database={1}; \
                           Trusted_Connection=yes" \
                           .format(self.servername,
                                   self.dbname))

        self.conn = conn 

        self.df = pd.read_sql(self.sql, conn)

    def writeJSON(self, df=None, jsonfile=None):
        """
        writeJSON - used to create a json file from a pandas dataframe
        for use in a sunburst plot.

        Parameters
        -----------------
        df: pandas dataframe, can contain multiple columns, beginning
        with most generic classification first, down to most specific
        classification (e.g. state, office, section, employee) - last
        column should be numerical value used to calculate proportion 
        for each class
        jsonfile: string, name of json output file

        Modified from:
        http://stackoverflow.com/questions/19317115/convert-flat-json-file-to-hierarchical-json-data-like-flare-json-d3-example-fil?rq=1

        """

        if not isinstance(df, pd.DataFrame):
            df = self.df
        if jsonfile == None:
            jsonfile = self.jsonfile

        dataStructure = {'name':'', 'children': []}

        for data in df.iterrows():

            current = dataStructure
            depthCursor = current['children']
            for i, item in enumerate(data[1][:-2]):
                idx = None
                j = None
                for j, c in enumerate(depthCursor):
                    if item in c.values():
                        idx = j
                if idx == None:
                    depthCursor.append({'name':item, 'children':[]})
                    idx = len(depthCursor) - 1 

                depthCursor = depthCursor[idx]['children']
                if i == len(data[1])-3:
                    depthCursor.append({'name':'{} {}'.format(data[1][-2], data[1][-1]),
                                        'size': data[1][-1]})

                current = depthCursor

        f = open(jsonfile, 'w')
        json.dump(dataStructure, f, indent=4)
        f.close()


