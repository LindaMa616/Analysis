#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 14:32:11 2018

@author: malinda
"""


def Data_Analysis(file):
    import pandas as pd
    #describe function could return the descriptive statistics that summarize the distribution 
    #if not adding include='all' inside describe(), it will only return the distribution of continous variables, if adding, it will also return the summary of discrete variables
    #transpose is to permute the dimensions
    data=pd.read_csv(file).describe(include='all').transpose()
    #.to_csv is used to export the data analysis results to working directory, the file name is 'Data_Analysis'
    data.to_csv('Data_Analysis.csv')
    return data
