#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 14:32:11 2018
"""


def Data_Analysis(file):
    import pandas as pd
    data=pd.read_csv(file)
    return data.describe(include='all')
