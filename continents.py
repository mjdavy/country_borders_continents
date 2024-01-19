import pandas as pd
import json
import numpy as np

countryExceptions = {
    'Antarctica': 'Antarctica',
    'Aland Islands': 'Europe',
    'Saint Barthelemy': 'North America',
    'Bouvet Island': 'Europe',
    'Western Sahara': 'Africa',
    'Guernsey': 'Europe',
    'South Georgia and the South Sandwich Islands': 'Antarctica',
    'Heard Island and McDonald Islands': 'Antarctica',
    'Jersey': 'Europe',
    'Saint Martin (French part)': 'North America',
    'Pitcairn' : 'Oceania',
    'Svalbard and Jan Mayen': 'Europe',
    'French Southern Territories': 'Antarctica' 
}

def find_continent(iso_3166_2, continents):
    # Iterate through each continent
    for continent, countries in continents.items():
        # Iterate through each country in the continent
        for country in countries:
            # Check if the ISO-3166-2 codes match
            if country['ISO-3166-2'] == iso_3166_2:
                return continent
    
    # Return None if no continent is found
    return None

def enrich_country_borders(json_file, continent_file):
    # Read the JSON files
    with open(json_file, 'r') as file:
        countries = json.load(file)
    
    with open(continent_file, 'r') as file:
        continents = json.load(file)
    
    # Create a dictionary to map ISO-3166-2 codes to continents
    iso_to_continent = {}
    for country in countries:
        iso_3166_2 = country['country_code']
        country_name = country['country_name']
        continent = find_continent(iso_3166_2, continents)
        if continent:
            iso_to_continent[iso_3166_2] = continent
            country['continent'] = continent
        else:
            # Check if the country is in the exceptions dictionary
            if country_name in countryExceptions:
                # check if the country is already in the iso_to_continent dictionary
                if iso_3166_2 in iso_to_continent: 
                    print(f'Overwriting {iso_3166_2} with {countryExceptions[country_name]}')
                continent = countryExceptions[country_name]
                iso_to_continent[iso_3166_2] = continent
                country['continent'] = continent
            else:
                print(f'No continent found for {country_name} ({iso_3166_2})')
    
    
    # Write the enriched data back to the JSON file
    with open(json_file, 'w') as file:
        json.dump(countries, file, indent=4)


def continents_excel_to_json():

    # Read the Excel file
    excel_file = pd.ExcelFile('continents.xlsx')

    # Initialize an empty dictionary to store the data
    data = {}

    # Iterate through each sheet in the Excel file
    for sheet_name in excel_file.sheet_names:
        # Read the sheet into a DataFrame
        df = excel_file.parse(sheet_name, header=1)
        
        # Check if the DataFrame has only one table
        if len(df.columns) == 4:  # Assuming there are 4 columns in the table
            # Extract the columns from the DataFrame
            countries = df['Country'].tolist()
            iso_3166_2 = df['ISO-3166-2'].astype(str).replace('nan', 'NA').tolist()
            iso_3166_3 = df['ISO-3166-3'].tolist()
            cctld = df['ccTLD'].replace(np.nan, '').tolist()
            
            # Create a list of dictionaries for each country
            country_data = []
            for i in range(len(countries)):
                country_dict = {
                    'name': countries[i],
                    'ISO-3166-2': iso_3166_2[i],
                    'ISO-3166-3': iso_3166_3[i],
                    'ccTLD': cctld[i]
                }
                country_data.append(country_dict)
            
            # Add the country data to the continent in the main dictionary
            data[sheet_name] = country_data

    # Write the data to a JSON file
    with open('continents.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

enrich_country_borders('country-borders.json', 'output.json')