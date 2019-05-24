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

for file in os.listdir(base_path):
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
fig, ax = plt.subplots(figsize=(12,6))
x = net_energy['year']
y = net_energy['net_MWh']
plt.plot(x,y, color='m')
plt.title('Average Net megawatt-hour(MWh) in California', fontsize=20)
ax.set_ylabel('Net MWh', fontsize=18)
ax.set_xlabel('Year', fontsize=18)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
#plt.savefig(base_path + r'\myfig.png')

#which companies are producing the greatest net MWh?
wind_energy['year'] = pd.to_datetime(wind_energy['year'], format='%Y')
sum_year_company = wind_energy.groupby(['year','company'], as_index=False).sum()
#highest producing companies: FPL Energy Operating Services Inc, Terra-Gen Operating Company, Seawest Energy Group

#plotting the average productions of the highest producing companies
fig, ax = plt.subplots(figsize = (12,6))
wind_energy[wind_energy['company'] == 'FPL Energy Operating Services Inc'].groupby('year')['net_MWh'].mean().plot(color = 'b', label='FPL Energy Operating Services Inc')
wind_energy[wind_energy['company'] == 'Terra-Gen Operating Company'].groupby('year')['net_MWh'].mean().plot(color = 'm', label='Terra-Gen Operating Company')
wind_energy[wind_energy['company'] == 'Seawest Energy Group'].groupby('year')['net_MWh'].mean().plot(color = 'g', label='Seawest Energy Group')
ax.legend(frameon=False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.title('Average Net MWh, Top Producing Companies', fontsize=20)
ax.set_ylabel('Net MWh', fontsize=18)
ax.set_xlabel('Year', fontsize=18)

#comparing total consumption in california and wind energy production
consumption = pd.read_csv(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\ca_electricity_consumption.csv')
total_consumption = consumption[consumption['Sector'] == 'Total']
total_consumption = total_consumption.drop(columns='Sector')
total_consumption = total_consumption.melt(id_vars='County', var_name='year', value_name='Consumption')
sum_consumption = total_consumption.groupby(['year'], as_index=False).sum()
#also possible to find the sum using: total_consumption.sum(axis=0), this just uses melt

#quick plot to see what is going on
fig, ax = plt.subplots(figsize=(12,6))
x = sum_consumption['year']
y = sum_consumption['Consumption']
plt.plot(x,y, color='m')

#see what percent wind energy accounts for each year 
net_to_merge = net_energy[['year', 'net_MWh']]
merged_data = pd.merge(net_to_merge, sum_consumption, on='year', how='right')


    