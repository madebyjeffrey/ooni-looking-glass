import csv
import os

class Country:
    def __init__(self, row):
        self.name = row[0]
        self.alpha2 = row[1]
        self.alpha3 = row[2]
        self.region = row[5]
        self.subregion = row[6]

country_list = []

with open(os.path.dirname(os.path.realpath(__file__)) + '/countries.csv') as csvfile:
    dialect = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    countries = csv.reader(csvfile, dialect)

    for line in countries:
        country_list.append(Country(line))

country_list_name = {}
country_list_alpha2 = {}
country_list_alpha3 = {}

for country in country_list:
    country_list_name[country.name] = country
    country_list_alpha2[country.alpha2] = country
    country_list_alpha3[country.alpha3] = country

def find_country_by_name(name):
    return country_list_name[name]

def find_country_by_code2(code):
    return country_list_alpha2[code]

def find_country_by_code3(code):
    return country_list_alpha3[code]

def find_countries_in_region(region):
    return [country for country in country_list if country.region.lower() == region.lower()]
