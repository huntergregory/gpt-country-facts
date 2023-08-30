## dependencies
from os.path import exists
from random import randint

## scrape country list from the britannica.com
# in bash: curl https://www.britannica.com/topic/list-of-countries-1993160 | grep -oP "place/[a-zA-Z\-]+" | grep -oP "/[a-zA-Z\-]+" | tr -d '/' > countries.txt
file_path = 'data/countries.txt'
if not exists(file_path):
    raise RuntimeError('{} not found. Please see curl command in countries.py on how to create this file'.format(file_path))

with open(file_path, 'r') as file:
    lines = file.readlines()
    all_countries = [line.strip().replace('-', ' ').title() for line in lines if line != '']

if len(all_countries) == 0:
    raise RuntimeError('No countries found in {}. Please see curl command in countries.py on how to create this file'.format(file_path))

random_country_index = randint(0, len(all_countries)-1)
