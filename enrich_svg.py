import xml.etree.ElementTree as ET
import pandas as pd
from fuzzywuzzy import fuzz
import re
import json

def load_csv_file(file_path):
    try:
        df = pd.read_csv(file_path, delimiter=';')
        return df
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
        return None

def load_svg_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing SVG file: {e}")
        return None

def clean_string(string):
    # Remove punctuation and whitespace
    cleaned_string = re.sub(r'[^\w\s]', '', string)
    # Convert to lowercase
    cleaned_string = cleaned_string.lower()
    return cleaned_string

def case_insensitive_match(country_name_svg, csv_df):
    cleaned_country_name_svg = clean_string(country_name_svg)
    for country_name_df in csv_df["Country or Area"]:
        cleaned_country_name_df = clean_string(country_name_df)
        if cleaned_country_name_svg == cleaned_country_name_df:
            print(f"Found exact match: {country_name_svg} == {country_name_df}")
            return country_name_df
    return None
    
def fuzzy_match_country_name(country_name_svg, csv_df):
    best_match = None
    best_ratio = 0
    for country_name_df in csv_df["Country or Area"]:
        ratio = fuzz.ratio(country_name_svg, country_name_df)
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = country_name_df
    return best_match, best_ratio

def log_failed_matches(failed_matches):
    if len(failed_matches) > 0:
        with open("failed_matches.json", "w") as file:
            json.dump(failed_matches, file)
        print("Failed matches logged in 'failed_matches.json' file.")

def update_svg_with_country_codes(svg_root, csv_df):
    failed_matches = []
    for element in svg_root.iter():
        if "id" in element.attrib and "d" in element.attrib:
            country_name_svg = element.attrib["id"]
            try:
                print(f"Updating country code for country name: {country_name_svg}")
                exact_match = case_insensitive_match(country_name_svg, csv_df)
                if exact_match is not None:
                    country_code = csv_df.loc[csv_df["Country or Area"] == exact_match, "ISO-alpha2 Code"].values
                    if len(country_code) > 0:
                        element.attrib["id"] = country_code[0]
                    else:
                        raise(f"Country code not found for country name: {exact_match}")
                else:
                    fuzzy_match, ratio = fuzzy_match_country_name(country_name_svg, csv_df)
                    failed_matches.append({"country_name_svg": country_name_svg, "fuzzy_match": fuzzy_match, "ratio": ratio, "id":""})
            except KeyError:
                print(f"Invalid column name in the CSV file.")
            except Exception as e:
                print(f"An error occurred while updating the SVG with country codes: {e}")
    
    log_failed_matches(failed_matches)

def save_svg_file(svg_root, file_path):
    try:
        # Replace nan values with a placeholder value
        for element in svg_root.iter():
            for key, value in element.attrib.items():
                if pd.isna(value):
                    element.attrib[key] = "N/A"

        tree = ET.ElementTree(svg_root)
        tree.write(file_path)
        print(f"Modified SVG file saved successfully: {file_path}")
    except ET.ParseError as e:
        print(f"Error saving SVG file: {e}")

def run():
    # load the svg world map
    svg_file_path = "world-low-complete.svg"
    svg_root = load_svg_file(svg_file_path)

    if svg_root is not None:
        print(f'loaded {svg_file_path} successfully. Root element: {svg_root}')

    # load the country data from the csv file
    csv_file_path = "UNSD.csv"
    csv_df = load_csv_file(csv_file_path)

    if csv_df is not None:
        print(f"Loaded {csv_file_path} successfully. DataFrame shape: {csv_df.shape}")

    # upddate the svg file with country codes matching the country names
    if svg_root is not None and csv_df is not None:
        # Update the SVG file with country codes
        update_svg_with_country_codes(svg_root, csv_df)

        # Save the modified SVG file
        modified_svg_file_path = "modified-world-map.svg"
        save_svg_file(svg_root, modified_svg_file_path)

if __name__ == "__main__":
    run()