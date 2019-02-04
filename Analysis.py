#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 14:32:11 2018

@author: malinda
"""

#type should only be excel or csv
def Data_Analysis(filename,typ):
    import pandas as pd
    if typ=='excel':
        data=pd.read_excel(filename).describe(include='all').transpose()
    else:
    #describe function could return the descriptive statistics that summarize the distribution 
    #if not adding include='all' inside describe(), it will only return the distribution of continous variables, if adding, it will also return the summary of discrete variables
    #transpose is to permute the dimensions
        data=pd.read_csv(filename).describe(include='all').transpose()
    #.to_csv is used to export the data analysis results to working directory, the file name is 'Data_Analysis'
    data.to_csv('Data_Analysis.csv')
    return data
