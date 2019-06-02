# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:12:05 2019

@author: User02
"""
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
my_ofile = r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\{}_wind_generation.csv'

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
    if not file.endswith('wind_generation.csv'):
        continue
    df = pd.read_csv(os.path.join(base_path, file))
    dfs.append(df)
    
wind_energy = pd.concat(dfs, axis=0, ignore_index=True)

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
plt.savefig(r'C:\Users\User02\Desktop\Harris\EnvironmentalPolicy\net_energy_plt.png')

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

#what percent of wind energy production is each company contributing 
#
#
#

#scrapping in electricity generation data
urls = ['https://www.energy.ca.gov/almanac/electricity_data/system_power/{}_gross_system_power.html'.format(year) for year in range(2002, 2007)]
otheryears = ['https://www.energy.ca.gov/almanac/electricity_data/system_power/{}_total_system_power.html'.format(year) for year in range(2007, 2016)]
lastyear = ['https://www.energy.ca.gov/almanac/electricity_data/total_system_power.html']
urls.extend(otheryears)
urls.extend(lastyear)

year_range = range(2002,2017)
zipped_years = zip(year_range,urls)

def get_rows_electric(response, year):
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    all_rows = table.find_all('tr')
    unparsed_rows = []
    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        row_lst = [val.text.replace(',','').replace('-','').replace('\xa0','') for val in td_tags]
        row_lst.append(str(year))
        unparsed_rows.append(row_lst)
    unparsed_rows = unparsed_rows[1:-1]
    return unparsed_rows   

#using the same as previous row_parser function
def row_parser(row):
    print (row)
    return ','.join(row)

my_ofile = r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\{}_electric_generation.csv'

for year, url in zipped_years:
    response = requests.get(url) 
    unparsed_rows = get_rows_electric(response, year)
    parsed_rows = [row_parser(row) for row in unparsed_rows] 
    if year < 2009:
        header = 'fuel_type,in_state_generation_GWh,northwest_imports_GWh,southwest_imports_GWh,gross_system_power,percent_gross_system_power,year'
    else:
        header = 'fuel_type,in_state_generation_GWh,percent_generation,northwest_imports_GWh,southwest_imports_GWh,energy_mix_GWh,power_mix,year'
    parsed_rows.insert(0, header)
    document = '\n'.join(parsed_rows)
    ofile_yr = my_ofile.format(year)
    print(ofile_yr)
    with open(ofile_yr, 'w') as ofile:
        ofile.write(document)

#importing electric generation data
base_path = r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi'

dfs = []

for file in os.listdir(base_path):
    if not file.endswith('electric_generation.csv'):
        continue
    df = pd.read_csv(os.path.join(base_path, file))
    dfs.append(df)
    
electric_energy = pd.concat(dfs, axis=0, ignore_index=True)

#get sums of annual electricity generation
def get_sums(df):
    df.loc[(df['in_state_generation_GWh'] == ' N/A ')] = 'nan'
    df['in_state_generation_GWh'] = df['in_state_generation_GWh'].apply(pd.to_numeric, errors='coerce')
    df = df.groupby(['year'], as_index=False).sum()
    df = df[:-1]
    return(df)

annual_generation = get_sums(electric_energy)

#comparing the wind energy data between the two data sets
#electric energy data
def wind_percent(df, sum_df):
    df = df.loc[(df['fuel_type']) == 'Wind']
    merged_data = pd.merge(sum_df, df, on='year', how='inner')
    merged_data['percent'] = merged_data['in_state_generation_GWh_y'] / merged_data['in_state_generation_GWh_x']
    merged_data['percent_pretty'] = merged_data['percent'].map(lambda c:'{}%'.format(round(c*100,2)))
    merged_data = merged_data[['year','percent','percent_pretty']]
    return(merged_data)
    
percent_wind = wind_percent(electric_energy, annual_generation)

#make a table

#wind energy data
#merged_data['Consumption'] = merged_data['Consumption'].apply(lambda x: x*1000)
#
#

#make a table

#graph the percentages together
#
#
#

#mapping by fuel type 
#
#
#

#ols regresstion
#
#
#


#total_consumption = total_consumption.drop(columns='Sector')
#total_consumption = total_consumption.melt(id_vars='County', var_name='year', value_name='Consumption')

 
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

pd.to_numeric(wind_energy['year'])
wind_model = smf.ols('net_MWh ~ year', data=wind_energy)
results = wind_model.fit()
results.summary()