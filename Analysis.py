#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 14:32:11 2018

@author: malinda
"""


def Data_Analysis(file):
    import pandas as pd
    data=pd.read_csv(file).describe(include='all').transpose()
    data.to_csv('Data_Analysis.csv')
    return data
