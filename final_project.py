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

#exporting csv
wind_energy.to_csv(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\CA_wind_energy_data.csv')

#net energy over time
net_energy = wind_energy.groupby('year', as_index=False).sum()

#plot
import matplotlib.pyplot as plt

def plot_net_wind(df):
    fig, ax = plt.subplots(figsize=(12,6))
    x = net_energy['year']
    y = net_energy['net_MWh']
    plt.plot(x,y, color='m')
    plt.title('Annual Net MWh (CA)', fontsize=20)
    ax.set_ylabel('Net MWh', fontsize=18)
    ax.set_xlabel('Year', fontsize=18)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.savefig(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\net_wind_energy_plt.png')

plot_net_wind(wind_energy)

plt.close()

#which companies are producing the greatest net MWh?
sum_year_company = wind_energy.groupby(['year','company'], as_index=False).sum()
#highest producing companies: FPL Energy Operating Services Inc, Terra-Gen Operating Company, Seawest Energy Group


#plotting the average productions of the highest producing companies

def plot_net_wind_company(df):
    fig, ax = plt.subplots(figsize = (12,6))
    wind_energy[wind_energy['company'] == 
                'FPL Energy Operating Services Inc'].groupby('year')['net_MWh'].mean().plot(color = 'b', label='FPL Energy Operating Services Inc')
    wind_energy[wind_energy['company'] == 
                'Terra-Gen Operating Company'].groupby('year')['net_MWh'].mean().plot(color = 'm', label='Terra-Gen Operating Company')
    wind_energy[wind_energy['company'] == 
                'Seawest Energy Group'].groupby('year')['net_MWh'].mean().plot(color = 'g', label='Seawest Energy Group')
    ax.legend(frameon=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.title('Average Net MWh, Top Producing Companies', fontsize=20)
    ax.set_ylabel('Net MWh', fontsize=18)
    ax.set_xlabel('Year', fontsize=18)
    plt.savefig(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\net_wind_company_energy_plt.png')
    
plot_net_wind_company(wind_energy)

plt.close()

#what percent of wind energy production is each company contributing? 
def percent_company_energy(df):
    annual_sum = df.groupby(['year'], as_index=False)['net_MWh'].agg({'total_sum':'sum'})
    company_sum = df.groupby(['year', 'company'], as_index=False)['net_MWh'].agg({'comp_sum':'sum'})
    merged_data = pd.merge(company_sum, annual_sum, on='year', how='left')
    merged_data['company_percent'] = merged_data['comp_sum'] / merged_data['total_sum']
    return(merged_data)
    
percent_company = percent_company_energy(wind_energy)
#Terra-Gen Operating Company top producing company between 2014-2018 
#producing between 21.1% - 23.2% of wind energy production

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

#getting the tables/using the parsing function and reading them in as csvs
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

electric_energy.to_csv(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\CA_electric_energy_data.csv')

#get sums of annual electricity generation 
def get_sums(df):
    df[(df['in_state_generation_GWh'] == ' N/A ')] = df[(df['in_state_generation_GWh'] == 'nan')]
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
    merged_data['electric_percent'] = merged_data['in_state_generation_GWh_y'] / merged_data['in_state_generation_GWh_x']
    merged_data['electric_percent_pretty'] = merged_data['electric_percent'].map(lambda c:'{}%'.format(round(c*100,2)))
    merged_data = merged_data[['year','electric_percent','electric_percent_pretty']]
    return(merged_data)
    
percent_wind = wind_percent(electric_energy, annual_generation)

#wind energy data
def compare_wind_percent(wind_df, electric_df, percent_wind):
    df_wind = wind_df.groupby(['year'],as_index=False).sum()
    df_electric = get_sums(electric_df)
    merged_data = pd.merge(df_electric, df_wind, on='year', how='right')
    merged_data['in_state_generation_GWh'] = merged_data['in_state_generation_GWh'].apply(lambda x:x*1000)
    merged_data['wind_percent'] = merged_data['net_MWh'] / merged_data['in_state_generation_GWh']
    merged_data['wind_percent_pretty'] = merged_data['wind_percent'].map(lambda c:'{}%'.format(round(c*100,2)))
    merged_data = merged_data[['year','wind_percent','wind_percent_pretty']]
    merged_percent_data = pd.merge(percent_wind, merged_data, on='year', how='right')
    merged_percent_data = merged_percent_data[:-3]
    merged_percent_data = merged_percent_data[['year','wind_percent_pretty','electric_percent_pretty']]
    return(merged_percent_data)
    
wind_energy_compared = compare_wind_percent(wind_energy, electric_energy, percent_wind)

#plotting by fuel type 
def clean_erroneous_fuel_types(df):
    df[(df['fuel_type'] == 'Coal 1')] = df[(df['fuel_type'] == 'Coal')]
    df[(df['fuel_type'] == 'Coal 2')] = df[(df['fuel_type'] == 'Coal')]
    df[(df['fuel_type'] == 'Solar 1')] = df[(df['fuel_type'] == 'Solar')]
    df[(df['fuel_type'] == 'Coal*')] = df[(df['fuel_type'] == 'Coal')]
    df[(df['fuel_type'] == 'Unspecified Sources of Power *')] = df[(df['fuel_type'] == 'Other')]
    df[(df['fuel_type'] == 'Unspecified Sources of Power')] = df[(df['fuel_type'] == 'Other')]
    df[(df['fuel_type'] == 'Unspecified Sources of Energy')] = df[(df['fuel_type'] == 'Other')]
    df[(df['fuel_type'] == 'Other (Petroleum Coke/Waste Heat)')] = df[(df['fuel_type'] == 'Other')]
    return(df)
    
electric_energy_clean = clean_erroneous_fuel_types(electric_energy)

#renewable energy sources 
def plot_renewables(df):
    fuel_types = ['Wind','Large Hydro', 'Renewables', 'Biomass','Geothermal','Solar','Small Hydro']
    colors = ['c','g','m','k','b','r','mediumvioletred']
    zipped_fuel = zip(fuel_types,colors)
    for types, colors in zipped_fuel:
        electric_energy[electric_energy['fuel_type'] ==
                    '{}'.format(types)].groupby('year')['in_state_generation_GWh'].mean().plot(color='{}'.format(colors),label='{}'.format(types))
        plt.ylabel('GWh', fontsize=10)
        plt.xlabel('Year', fontsize=10)
        plt.title('Annual in State Renewable Energy Production (CA)', fontsize=15)
        plt.legend(frameon=False, loc='best', fontsize='small')
        plt.savefig(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\renewable_energy_plt.png')


plot_renewables(electric_energy)  

plt.close()

#non-renewable energy sources
def plot_nonrenewables(df):
    fuel_types = ['Coal','Natural Gas', 'Nuclear', 'Oil']
    colors = ['c','g','m','r']
    zipped_fuel = zip(fuel_types,colors)
    for types, colors in zipped_fuel:
        electric_energy[electric_energy['fuel_type'] ==
                    '{}'.format(types)].groupby('year')['in_state_generation_GWh'].mean().plot(color='{}'.format(colors),label='{}'.format(types))
        plt.ylabel('GWh', fontsize=10)
        plt.xlabel('Year', fontsize=10)
        plt.title('Annual in State Renewable Energy Production (CA)', fontsize=15)
        plt.legend(frameon=False, loc='best', fontsize='small')
        plt.savefig(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\non_renewable_energy_plt.png')
        
plot_nonrenewables(electric_energy)    

plt.close()

#function for the plot
def plot_all_energy(df):
    renewable_fuel = ['Wind', 'Renewables', 'Biomass','Geothermal','Solar','Small Hydro','Large Hydro'] 
    non_renewable_fuel = ['Coal', 'Nuclear', 'Oil','Natural Gas']
    zipped = zip(renewable_fuel,non_renewable_fuel)    
    for renewable_fuel, non_renewable_fuel in zipped:
        electric_energy[electric_energy['fuel_type'] ==
                    '{}'.format(renewable_fuel)].groupby('year')['in_state_generation_GWh'].mean().plot(color='g',label='{}'.format(renewable_fuel))                        
        electric_energy[electric_energy['fuel_type'] ==
                     '{}'.format(non_renewable_fuel)].groupby('year')['in_state_generation_GWh'].mean().plot(color='m',label='{}'.format(non_renewable_fuel))                       
        plt.ylabel('GWh', fontsize=10)
        plt.xlabel('Year', fontsize=10)                        
        plt.title('Annual in State Energy Production (CA)', fontsize=15)
        plt.legend(frameon=False, loc='best', fontsize='small') 
        plt.savefig(r'C:\Users\User02\Documents\GitHub\spring-2019-final-project-rei-bertoldi\all_energy_plt.png')
           
        
plot_all_energy(electric_energy)

plt.close()

#running an OLS regression line
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

electric_model = smf.ols('in_state_generation_GWh ~ year + fuel_type', data=electric_energy)
electric_results = electric_model.fit()
electric_results.summary()
#regression says that an increas in year is associated with an increase in 17 GWh of production, controlling for fuel type 
#the coefficient on wind fuel is 1442 GWh of production
