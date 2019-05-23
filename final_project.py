# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:12:05 2019

@author: User02
"""
#summarize the data with plots, tables and summary statistics, 
#and then fit a simple model to it using Numpy or Statsmodels

#importing 
import requests
from bs4 import BeautifulSoup

#setting the url
url = 'https://www.energy.ca.gov/almanac/renewables_data/wind/index.php'

#creating a function to get the data and clean it
def get_rows(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    all_rows = table.find_all('tr')
    unparsed_rows = []
    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        unparsed_rows.append([val.text.replace(',','') for val in td_tags])
    unparsed_rows = unparsed_rows[1:-1]
    return unparsed_rows    

#row parsing function
def row_parser(row):
    return ','.join(row)

#creating a loop to export the csvs for all the years
my_ofile = r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\{}.csv'

for year in range(2003, 2019):
    year = str(year)
    response = requests.post(url, data={'newYear':year})
    unparsed_rows = get_rows(response)
    parsed_rows = [row_parser(row) for row in unparsed_rows]
    header = 'year,company,eia_id,cec_id,plant,state,capacity_MW,gross_MWhm,net_MWh'
    parsed_rows.insert(0, header)
    document = '\n'.join(parsed_rows)
    ofile_yr = my_ofile.format(year)
    with open(ofile_yr, 'w') as ofile:
        ofile.write(document)

#importing and merging data
import os
import pandas as pd
base_path = r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi'

dfs = []

for file in os.listdir(path):
    if not file.endswith('.csv'):
        continue
    df = pd.read_csv(os.path.join(base_path, file))
    dfs.append(df)
    
wind_energy = pd.concat(dfs, axis=0, ignore_index=True)
len(wind_energy.index.values)
#net energy over time
net_energy = wind_energy.groupby('year', as_index=False).sum()
#plot
import matplotlib.pyplot as plt

#looking at the contributions of each company 
unique_values = wind_energy.groupby(['year', 'company']).size().reset_index().rename(columns={0:'unique'})
#big four:
    #foundation wind power
    #terra-gen operating company
    #FPL energy
    #seawest 
    
company_energy = wind_energy.groupby(['company','year'], as_index=False)['net_MWh'].sum()
filtered_energy = company_energy[company_energy["company"].isin([""]), :]





#
    

    