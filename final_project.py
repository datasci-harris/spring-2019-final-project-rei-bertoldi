# -*- coding: utf-8 -*-
"""
Created on Fri May 17 12:12:05 2019

@author: User02
"""
#testing and creating the parsing function
import requests
from bs4 import BeautifulSoup

url = 'https://www.energy.ca.gov/almanac/renewables_data/wind/index.php'

response = requests.get(url) 

#these need to be put into a function

def get_rows(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    all_rows = table.find_all('tr')
    unparsed_rows = []
    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        unparsed_rows.append([val.text.replace(',','') for val in td_tags])
    unparsed_rows = unparsed_rows[1:-1]

def row_parser(row):
    return ','.join(row)

parsed_rows = [row_parser(row) for row in unparsed_rows]

header = 'year, company, eia_id, cec_id, plant, state, capacity_MW, gross_MWhm, net_MWh'
parsed_rows.insert(0, header)

#this probably can be outside of the function
document = '\n'.join(parsed_rows)

path = r'C:\Users\User02\Desktop\Harris\Programming\test.csv'

with open(path, 'w') as ofile:
    ofile.write(document)
    
#write this damn function


#looping the csvs in a loop

my_ofile = 'path\{}.csv'

for year in ['2018', '2017', '2016]:
    response = requests.post(url, data={'newYear':year})
#    soup = BeautifulSoup(response.text, 'html.parser')
    parsed_data = my_parsing_function(response)
    with open(my_ofile, 'w') as ofile:
        ofile.write(parsed_data)