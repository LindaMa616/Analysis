#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 21:51:41 2019

@author: malinda
"""
import pandas as pd
global pd

def main():

    df1=pd.read_excel('ParccMathDistribGrade6.xlsx')[['SchZip','Code','Latitude','Longitude','MetExceed']].dropna() #School Data aka GapSchool
    df1.MetExceed=df1.iloc[:,4].map(lambda x: 100-x)#since we only have MetExceed percentage, we want fail percent. change the last column to fail percent
    df1.rename(columns={'MetExceed':'MathScoreFailPercent'},inplace=True)#change the columns name from MetExceed to MathScoreFailPercent
    df1.SchZip=df1.SchZip.apply(str).map(lambda x:x[:5])#since the zip data is not clean, some zip code includes sub zip code, get pervious 5 digits.
    df1.rename(columns={'SchZip':'Zip'},inplace=True)#Change the name from 'SchZip' to 'Zip' in order to combine multiple DataFrame in Future
    df2=pd.read_excel('Zip_Data.xlsx',converters={'Zip': str})[['Zip','Median Income']].dropna()#Income Data aka GapZip
    df2.rename(columns={'Median Income':'MedianIncome'},inplace=True)#Change the name from Median Income to MedianIncome since space could not appear in variable name
    df3=pd.read_excel('Copy of NJ Club List.xls.xlsx',converters={'Primary Zip/Postal Code': str})[['Primary Zip/Postal Code','Club Name','Club Status']].dropna()#NJ Club Data And First Robotics Data
    df3.rename(columns={'Primary Zip/Postal Code':'Zip'},inplace=True)
    df3=df3[df3['Club Status']=='Active']#filter NJ Club, only keep active clubs
    df3=df3.drop(['Club Status'],axis=1)#then drop Club Status Column, we don't need it anymore
    df4=pd.read_excel('FIRST Robotics Teams.xlsx')[['Zipcode','Team Name']].dropna()
    df4.rename(columns={'Zipcode':'Zip'},inplace=True)
    NeedIndexScore=needIndexScoreAlgorithm(df1,df2,df3,df4) #To get need index score with previous 4 files
    df5=pd.read_excel('Copy of DataCollection Resource Tracking [https___link.run_data.tracker].xlsx','CollegesDataTracker')[['CollegeCode','Zip','Lat','Lon','Enrollment']].dropna() #College Data
    df5.Zip=df5.Zip.apply(lambda x:x[:5])#get previous 5 digits in Zip Code
    df5.rename(columns={'Zip':'zip'},inplace=True)
    df6=pd.read_excel('GapCompany Revised.xlsx',converters={'Zip': str})[['Zip','Code','Latitude','Longitude','Employees']].dropna()#Company Data
    df6['Zip']=df6.Zip.apply(lambda x:'0'+x)#the zip code always be read without leading 0, I concat them together
    df6.rename(columns={'Code':'CompanyCode','Latitude':'Lat','Longitude':'Lon','Zip':'zip'},inplace=True)
    df7=pd.read_excel('GapLibrary Revised.xlsx',converters={'Zip': str})[['Zip','Code','Lat','Lon']].dropna()#Library Data
    df7['Zip']=df7.Zip.apply(lambda x: '0'+x)
    df7.rename(columns={'Code':'libraryCode','Zip':'zip'},inplace=True) 
    df_target=NeedIndexScore[['Zip','Code']]
    ServiceAbilityIndexScore=serviceAbilityScoreAlgorithm(df_target,5,df5,df6,df7)
    df=pd.merge(NeedIndexScore,ServiceAbilityIndexScore,on='Code',how='right')
    writerdf=pd.ExcelWriter('TargetIndexScore.xlsx')
    df.to_excel(writerdf,index=False)
    
def needIndexScoreAlgorithm(GapSchool,GapZip,GapNJClubList,GapFirstRoboticsTeam):
    NeedIndexSchoolScore=needIndexSchoolScoreMap(GapSchool,25,40,55,75)
    NeedIndexZipIncome=needIndexIncomeScoreMap(GapZip,30000,60000,90000,125000)
    NeedIndexZipOffering=needIndexOfferingMap(GapNJClubList,GapFirstRoboticsTeam,0,1,3,5)
    NeedIndexScore=NeedIndexSchoolScore.merge(NeedIndexZipIncome,on='Zip').merge(NeedIndexZipOffering,on='Zip')
    NeedIndexScore['NeedIndexTotalScore']=NeedIndexScore.apply(lambda row:row.NeedIndexSchoolScore+row.NeedIndexZipIncome+row.NeedIndexZipOffering,axis=1)
    target=NeedIndexScore[NeedIndexScore.NeedIndexTotalScore>=100].sort_values(['NeedIndexTotalScore'],ascending=[False]).reset_index(drop=True)
    return target

def serviceAbilityScoreAlgorithm(target,distance,CollegeEnrollment,GapCompany,GapLibrary):
    from pyzipcode import ZipCodeDatabase
    zcdb = ZipCodeDatabase()
    DF=pd.DataFrame(columns=['Zip','zip'])
    center=target['Zip'].unique()
    for i in center:
        in_radius=[z.zip for z in zcdb.get_zipcodes_around_radius(i,distance)] # ('ZIP', radius in miles)
        df=pd.DataFrame({'zip':in_radius})
        df['Zip']=i
        DF=DF.append(df,ignore_index=True)
    school_college_distance=Distance(target,CollegeEnrollment,DF)
    writerschool_college_distance=pd.ExcelWriter('school_college_distance.xlsx')
    school_college_distance.to_excel(writerschool_college_distance,index=False)
    
    school_company_distance=Distance(target,GapCompany,DF)
    writerschool_company_distance=pd.ExcelWriter('school_company_distance.xlsx')
    school_company_distance.to_excel(writerschool_company_distance,index=False)
    
    
    school_library_distance=Distance(target,GapLibrary,DF)
    writerschool_library_distance=pd.ExcelWriter('school_library_distance.xlsx')
    school_library_distance.to_excel(writerschool_library_distance,index=False)
    
    ServiceAbilityIndexCollegeNearby=serviceAbilityIndexCollegeMap(school_college_distance,0,200,1000)
    ServiceAbilityIndexCompanyNearby=serviceAbilityIndexCompanyMap(school_company_distance,0,200,1000)
    ServiceAbilityIndexHostNearby=serviceAbilityIndexLibraryMap(school_library_distance,1,5)
    ServiceAbilityIndexScore=ServiceAbilityIndexCollegeNearby.merge(ServiceAbilityIndexCompanyNearby,on='Code',left_index=True).merge(ServiceAbilityIndexHostNearby,on='Code',left_index=True)
    ServiceAbilityIndexScore['ServiceAbilityIndexTotalScore']=ServiceAbilityIndexScore.apply(lambda row: row.ServiceabilityIndexCollegeNearby+row.ServiceabilityIndexCompanyNearby+row.ServiceabilityIndexLibraryNearby,axis=1)
    target=ServiceAbilityIndexScore[ServiceAbilityIndexScore.ServiceAbilityIndexTotalScore>=100].sort_values(['ServiceAbilityIndexTotalScore'],ascending=[False]).reset_index(drop=True)
    return target
    #ServiceAnilityIndexScore['ServiceAbilityIndexTotalScore']=
    
    
def needIndexSchoolScoreMap(GapSchool,p1,p2,p3,p4):
    GapSchool['NeedIndexSchoolScore']=GapSchool.MathScoreFailPercent.apply(lambda x: 0 if x>=0 and x<p1 else(25 if x>=p1 and x<p2 else(50 if p2<=x and x<p3 else (75 if x>=p3 and x<p4 else 100))))
    return GapSchool

def needIndexIncomeScoreMap(GapZip,p1,p2,p3,p4):
    NeedIndex=GapZip[['Zip']]
    NeedIndex['NeedIndexZipIncome']=GapZip.MedianIncome.apply(lambda x: 100 if x>=0 and x<p1 else(75 if x>=p1 and x<p2 else(50 if x>=p2 and x<p3 else(25 if x>=p3 and x<p4 else 0))))
    return NeedIndex
    
def needIndexOfferingMap(GapNJClubList,GapFirstRoboticsTeam,p1,p2,p3,p4):
    df_NJClub=GapNJClubList.groupby('Zip').count().reset_index()
    df_NJClub.rename(columns={'Club Name':'Number'},inplace=True)
    df_FirstRoboticsTeam=GapFirstRoboticsTeam.groupby('Zip').count().reset_index()
    df_FirstRoboticsTeam.rename(columns={'Team Name':'Number'},inplace=True)
    df_club=pd.concat([df_NJClub,df_FirstRoboticsTeam]).groupby('Zip').sum().reset_index()
    NeedIndex=df_club[['Zip']]
    NeedIndex['NeedIndexZipOffering']=df_club.Number.apply(lambda x:100 if x>=0 and x<p1 else(75 if x>=p1 and x<p2 else(50 if x>=p2 and x<p3 else(25 if x>=p3 and x<=p4 else 0))))
    return NeedIndex

def serviceAbilityIndexCollegeMap(CollegeEnrollment,p1,p2,p3):
    CollegeEnrollment=CollegeEnrollment[['Code','Enrollment']]
    CollegeEnrollment=CollegeEnrollment.groupby('Code').sum().reset_index()
    #CollegeEnrollment['Enrollment']=CollegeEnrollment['Enrollment'].apply(pd.to_numeric)
    CollegeEnrollment['ServiceabilityIndexCollegeNearby']=CollegeEnrollment.Enrollment.apply(lambda x:0 if x>=0 and x<p1 else(20 if x>=p1 and x<p2 else(50 if x>=p2 and x<p3 else 100)))
    return CollegeEnrollment

def serviceAbilityIndexCompanyMap(CompanyEmployee,p1,p2,p3):
    CompanyEmployee=CompanyEmployee[['Code','Employees']]
    CompanyEmployee=CompanyEmployee.groupby('Code').sum().reset_index()
    CompanyEmployee['ServiceabilityIndexCompanyNearby']=CompanyEmployee.Employees.apply(lambda x:0 if x>=0 and x<p1 else(20 if x>=p1 and x<p2 else(50 if x>=p2 and x<p3 else 100)))
    return CompanyEmployee

def serviceAbilityIndexLibraryMap(Library,p1,p2):
    Library=Library[['Code','libraryCode']]
    Library=Library.groupby('Code').count().reset_index()
    Library.rename(columns={'libraryCode':'Libraries'},inplace=True)
    Library['ServiceabilityIndexLibraryNearby']=Library.Libraries.apply(lambda x:0 if x>=0 and x<p1 else(50 if x>=p1 and x<p2 else 100))
    return Library

def Distance(school,service,zipCodeInRadius):    
    #make a temporary column in both dataframe, in order to perform cross join on the column
    school['temp']=1
    service['temp']=1
    D=school.merge(service,on='temp')
    D.drop('temp',axis=1,inplace=True)
    D=pd.merge(D,zipCodeInRadius,on=['Zip','zip'],how='inner')
    #D['distance']=D.apply(lambda row: haversine_formula(row.Latitude,row.Longitude,row.Lat,row.Lon),axis=1)
    return D

def haversine_formula(lat_school,lon_school,lat_service,lon_service):    
    from math import sin, cos, sqrt,atan2,radians
    #approximate radius of earth in miles 
    R = 3959
    #convert decimal degrees to radians 
    lat1,lon1,lat2,lon2=map(radians,[lat_school,lon_school,lat_service,lon_service])
     # haversine formula
    dlat,dlon=lat2-lat1,lon2-lon1
    a=sin(dlat/2)**2+cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c=2*atan2(sqrt(a),sqrt(1-a))
    distance=R*c
    return distance


    
main()