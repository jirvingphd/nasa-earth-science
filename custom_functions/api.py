"""Complete workflow
specs = '''Select a region that will be a perfect example of the effects of urban heat islands.
Select small identically-sized nearby non-overlapping regions from 2 separate census FIPS counties
the selected area to minimize the size of the dataset.'''
# Select a region in a non-desert area.
# 

chatgpt_params = suggest_data_params(specs=specs,pydantic_model=DataParamsFips, return_json=True, temperature=0.0)
print(chatgpt_params)

display(preview_regions(chatgpt_params))

## Get urban data
urban_census_block_fips = fetch_census_block_data(chatgpt_params['coordinates']['urban'], only_block_fips=True, censusYear=2020)
print(f"{urban_census_block_fips=}")

urban_data = get_census_data_for_block(urban_census_block_fips)
urban_data['Region'] = 'Urban'

## Get rural data
rural_census_block_fips = fetch_census_block_data(chatgpt_params['coordinates']['rural'], only_block_fips=True, censusYear=2020)
print(f"{rural_census_block_fips=}")

rural_data = get_census_data_for_block(rural_census_block_fips)
rural_data['Region'] = 'Rural'
rural_dat
"""
import os
import requests
import pandas as pd
from IPython.display import display



# def search_and_download(region_name, bounding_box, time_range, token, dest_folder='./data/MODIS-LST/',
#                         force_download=False):
#     """
#     Searches for granules using the NASA Earthdata API and downloads the data files for a given region.

#     Args:
#         region_name (str): The name of the region.
#         bounding_box (dict): The bounding box coordinates of the region in the format {'SW': [lat, lon], 'NE': [lat, lon]}.
#         time_range (dict): The temporal range of the data in the format {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}.
#         token (str): The access token for the NASA Earthdata API.
#         dest_folder (str, optional): The destination folder to save the downloaded data files. Defaults to './data/MODIS-LST/'.

#     Returns:
#         list: A list of dictionaries containing the region name and the URL of each downloaded data file.
#     """
#     # Base URL for searching granules
#     search_url = 'https://cmr.earthdata.nasa.gov/search/granules.json'
    
#     # Pagination settings
#     page_size = 10
#     page_num = 1
#     total_hits = None

#     # List to store entries and links
#     entries_links = []

#     while True:
#         # Set up the parameters for the search query
#         params = {
#             'short_name': 'MOD11A2',  # Dataset short name
#             'version': '061',         # Dataset version
#             'temporal': f"{time_range['start']},{time_range['end']}",  # Temporal range
#             'bounding_box': f"{bounding_box['SW'][1]},{bounding_box['SW'][0]},{bounding_box['NE'][1]},{bounding_box['NE'][0]}",  # Bounding box coordinates
#             'page_size': page_size,   # Number of results per page
#             'page_num': page_num      # Current page number
#         }
        
#         # Authorization header with the token
#         headers = {
#             'Authorization': f'Bearer {token}'
#         }

#         # Send the request to the NASA Earthdata API
#         response = requests.get(search_url, params=params, headers=headers)

#         if response.status_code == 200:
#             # Parse the JSON response
#             data = response.json()


#             ## JMI: Confirm this total_hits code works as expected
#             # Determine the total number of hits on the first request
#             if total_hits is None:
#                 total_hits = int(response.headers.get('CMR-Hits', 0))
#                 print(f"Total hits for {region_name}: {total_hits}")

#             # Check if there are entries in the response
#             if data['feed']['entry']:
#                 for entry in data['feed']['entry']:
#                     # Extract relevant metadata from each entry
#                     granule_id = entry.get('id', 'N/A')
#                     dataset_id = entry.get('dataset_id', 'N/A')
#                     start_time = entry.get('time_start', 'N/A')
#                     end_time = entry.get('time_end', 'N/A')
#                     spatial_extent = entry.get('boxes', ['N/A'])[0]
                    
                    
#                     # Extract the data links for downloading
#                     data_links = [link['href'] for link in entry['links'] if 'data#' in link['rel']]
                    
#                     # Download each data link and store the entries and links
#                     for url in data_links:
#                         dir_for_dl = os.path.join(dest_folder, region_name)
#                         # Define the filename based on the URL (to check if the file is a directory)
#                         filename = os.path.join(dir_for_dl,#dest_folder, 
#                                                 url.split('/')[-1])
                        
                
#                         # Check if directory
#                         if os.path.isdir(filename):
#                             print(f"- Skipping directory {filename}")
#                             continue
                        
#                         if "s3credentials" in filename:
#                             print(f"- Skipping S3 credentials link {filename}")
#                             continue
                        
#                         if '?p' in filename:
#                             print(f"- Skipping link with query parameters {filename}")
#                             continue
#                         # Remove question marks
#                         filename = filename.replace("?", "-")
                        
                        
#                         filepath = download_file(url, dir_for_dl, token, force_download=force_download)
#                         entries_links.append({'region': region_name, 'url': url,"fpath":filepath, 'granule_id': granule_id, 'dataset_id': dataset_id,
#                                             'start_time': start_time, 'end_time': end_time, 'spatial_extent': spatial_extent})
#                         # print("\n")
#             else:
#                 print(f"\n[!] No entries found for region: {region_name}")

#             # Check if we have fetched all results
#             if page_num * page_size >= total_hits:
#                 break
#             else:
#                 page_num += 1
#         else:
#             print(f"\n[!] Error: {response.status_code} - {response.text}")
#             break

#     return entries_links


# def download_file(url, dest_folder, token, force_download=False):
#     """
#     Downloads a file from the given URL and saves it to the specified destination folder.

#     Args:
#         url (str): The URL of the file to download.
#         dest_folder (str): The destination folder where the file will be saved.
#         token (str): The authorization token for accessing the file.
#         force_download (bool, optional): If set to True, the file will be downloaded even if it already exists in the destination folder. Defaults to False.

#     Returns:
#         str: The path of the downloaded file.

#     Raises:
#         None

#     """
#     # Create the destination folder if it doesn't exist
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
    
#     # Define the filename based on the URL
#     filename = os.path.join(dest_folder, url.split('/')[-1])
    
#     # Check if the file already exists
#     if os.path.exists(filename) and not force_download:
#         print(f"- File {filename} already exists, skipping download.")
#         return filename

#     # Authorization header with the token
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
    
#     try:
#         # Send the request to download the file
#         response = requests.get(url, headers=headers)
        
#     except Exception as e:
#         print(f"- [!] An error occurred while downloading {url}: {e}")
#         return
    
#     # Save the file if the request is successful
#     if response.status_code == 200:
#         with open(filename, 'wb') as f:
#             f.write(response.content)
#         print(f"- Downloaded {filename}")
#     else:
#         print(f"- [!] Failed to download {url}: {response.status_code}")
    
#     return filename


def search_and_download(region_name, bounding_box, time_range, token, dest_folder='./data/MODIS-LST/',
                        force_download=False, verbose=True, day_night='unspecified'):
    """
    Searches for granules using the NASA Earthdata API and downloads the data files for a given region.

    Args:
        region_name (str): The name of the region.
        bounding_box (dict): The bounding box coordinates of the region in the format {'SW': [lat, lon], 'NE': [lat, lon]}.
        time_range (dict): The temporal range of the data in the format {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}.
        token (str): The access token for the NASA Earthdata API.
        dest_folder (str, optional): The destination folder to save the downloaded data files. Defaults to './data/MODIS-LST/'.

    Returns:
        list: A list of dictionaries containing the region name and the URL of each downloaded data file.
    """
    # Base URL for searching granules
    search_url = 'https://cmr.earthdata.nasa.gov/search/granules.json'
    
    # Pagination settings
    page_size = 10
    page_num = 1
    total_hits = None

    # List to store entries and links
    entries_links = []

    while True:
        # Set up the parameters for the search query
        params = {
            'short_name': 'MOD11A2',  # Dataset short name
            'version': '061',         # Dataset version
            'temporal': f"{time_range['start']},{time_range['end']}",  # Temporal range
            'bounding_box': f"{bounding_box['SW'][1]},{bounding_box['SW'][0]},{bounding_box['NE'][1]},{bounding_box['NE'][0]}",  # Bounding box coordinates
            'page_size': page_size,   # Number of results per page
            'page_num': page_num      # Current page number
        }

        # Authorization header with the token
        headers = {
            'Authorization': f'Bearer {token}'
        }

        # Send the request to the NASA Earthdata API
        response = requests.get(search_url, params=params, headers=headers)
        

        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()


            ## JMI: Confirm this total_hits code works as expected
            # Determine the total number of hits on the first request
            if total_hits is None:
                total_hits = int(response.headers.get('CMR-Hits', 0))
                print(f"Total hits for {region_name}: {total_hits}")

            # Check if there are entries in the response
            if data['feed']['entry']:
                for entry in data['feed']['entry']:
                    # Extract relevant metadata from each entry
                    granule_id = entry.get('id', 'N/A')
                    dataset_id = entry.get('dataset_id', 'N/A')
                    start_time = entry.get('time_start', 'N/A')
                    end_time = entry.get('time_end', 'N/A')
                    spatial_extent = entry.get('boxes', ['N/A'])[0]
                    
                    
                    # Extract the data links for downloading
                    data_links = [link['href'] for link in entry['links'] if 'data#' in link['rel']]
                    
                    # Download each data link and store the entries and links
                    for url in data_links:
                        dir_for_dl = os.path.join(dest_folder, region_name)
                        # Define the filename based on the URL (to check if the file is a directory)
                        filename = os.path.join(dir_for_dl,#dest_folder, 
                                                url.split('/')[-1])
                        
                
                        # Check if directory
                        if os.path.isdir(filename):
                            if verbose:
                                print(f"- Skipping directory {filename}")
                            continue
                        
                        if "s3credentials" in filename:
                            if verbose:
                                print(f"- Skipping S3 credentials link {filename}")
                            continue
                        
                        if '?p' in filename:
                            if verbose:
                                print(f"- Skipping link with query parameters {filename}")
                            continue
                        # Remove question marks
                        filename = filename.replace("?", "-")
                        
                        
                        filepath = download_file(url, dir_for_dl, token, force_download=force_download, 
                                                 params=dict(day_night=day_night),
                                                 verbose=True # Always be verbose for download
                                                 )
                        entries_links.append({'region': region_name, 'url': url,"fpath":filepath, 'granule_id': granule_id, 'dataset_id': dataset_id,
                                            'start_time': start_time, 'end_time': end_time, 'spatial_extent': spatial_extent})
                        # print("\n")
            else:
                print(f"\n[!] No entries found for region: {region_name}")

            # Check if we have fetched all results
            if page_num * page_size >= total_hits:
                break
            else:
                page_num += 1
        else:
            print(f"\n[!] Error: {response.status_code} - {response.text}")
            break

    return entries_links


def download_file(url, dest_folder, token, force_download=False, verbose=True, params={}):
    """
    Downloads a file from the given URL and saves it to the specified destination folder.

    Args:
        url (str): The URL of the file to download.
        dest_folder (str): The destination folder where the file will be saved.
        token (str): The authorization token for accessing the file.
        force_download (bool, optional): If set to True, the file will be downloaded even if it already exists in the destination folder. Defaults to False.

    Returns:
        str: The path of the downloaded file.

    Raises:
        None

    """
    # Create the destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Define the filename based on the URL
    filename = os.path.join(dest_folder, url.split('/')[-1])
    
    # Check if the file already exists
    if os.path.exists(filename) and not force_download:
        if verbose:
            print(f"- File {filename} already exists, skipping download.")
        return filename

    # Authorization header with the token
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        # Send the request to download the file
        response = requests.get(url, headers=headers, params=params)
        
    except Exception as e:
        print(f"- [!] An error occurred while downloading {url}: {e}")
        return
    
    # Save the file if the request is successful
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        if verbose:
            print(f"- Downloaded {filename}")
    else:
        print(f"- [!] Failed to download {url}: {response.status_code}")
    
    return filename


def process_all_files_df(all_files_df, parse_and_clean_xml=True, save_to_csv=True, csv_fpath="./data/MODIS-LST/files_df.csv"):
    """
    Process all files in the given DataFrame.
    Args:
        all_files_df (DataFrame): The DataFrame containing information about all files.
        parse_and_clean_xml (bool, optional): Whether to parse and clean XML files. Defaults to True.
        save_to_csv (bool, optional): Whether to save the processed DataFrame to a CSV file. Defaults to True.
        csv_fpath (str, optional): The file path to save the CSV file. Defaults to "./data/MODIS-LST/files_df.csv".
    Returns:
        DataFrame: The processed DataFrame.
    """
    
    # Remove duplicate files
    files_df = all_files_df.drop_duplicates(subset=['fpath'])

    # Saving the type of file
    files_df['type'] = files_df['fpath'].apply(lambda x: x.split('.')[-1])
    
    # Filtering by Type
    files_df = files_df[files_df['type'].isin(['hdf','xml'])]
    
    
    # Save fname without extension for grouping xml and hdf files
    def remove_extension(fpath):
        return fpath.replace('.cmr.xml','').replace('.hdf','')
    files_df['fname'] = files_df['fpath'].apply(remove_extension)
    
    
    # Group Files by fname stub (without extension)
    grouped_files = files_df.groupby('fname')['fpath'].apply(lambda x: ";".join(x))#.values)
    grouped_files = grouped_files.to_frame('fpaths_combined')#.reset_index()
    
    # Split the fpaths_combined into separate columns
    grouped_files[['.hdf_file','.xml_file']] = grouped_files['fpaths_combined'].str.split(";", expand=True)
    grouped_files = grouped_files.drop(columns=['fpaths_combined']).reset_index()
    
    # Merge the grouped files back to the original files_df
    file_cols = files_df.drop(columns=['url','type','fpath'], errors='ignore').columns # ['region','fname','fpath','']
    hdf_files_df = files_df.loc[files_df['type']=='hdf', file_cols]
    files_df = pd.merge(hdf_files_df,grouped_files, on='fname', how='left')
    files_df = files_df.set_index('fname')
    
    # Save the xml file info to the dataframe
    if parse_and_clean_xml:
        from .xml import parse_and_clean_xml_file
        xml_df = files_df['.xml_file'].apply(parse_and_clean_xml_file, as_series=True)
        files_df_with_xml = pd.concat([files_df, xml_df], axis=1)

        # Convert the lat/lon range to a list of lat and lon ranges
        def get_lat_lon_range(row):
            sw_lat, sw_lon = row['Spatial_Coordinates__SW']
            ne_lat, ne_lon = row['Spatial_Coordinates__NE']
            return [sw_lat, ne_lat], [sw_lon, ne_lon]
        files_df_with_xml['lat_range'], files_df_with_xml['lon_range'] = zip(*files_df_with_xml.apply(get_lat_lon_range, axis=1))
        # Rename for consistency
        files_df = files_df_with_xml
    
    if save_to_csv:
        print(f"- Saving files_df to {csv_fpath}")
        files_df.to_csv(csv_fpath)
    
    return files_df


import requests
import pandas as pd
def fetch_census_block_data(coordinates, censusYear=2020,only_block_fips=False):
    """
    Fetches census block data based on the given coordinates.
    Parameters:
    - coordinates (dict or tuple): The coordinates of the location. If a dictionary is provided, it should contain 'SW' and 'NE' keys representing the southwest and northeast coordinates respectively. If a tuple is provided, it should contain the latitude and longitude values.
    - censusYear (int): The year for which the census data is requested. Default is 2020.
    - only_block_fips (bool): If True, only the block FIPS code will be returned. If False, the entire response will be returned. Default is False.
    Returns:
    - census_block_fips (str): The block FIPS code if only_block_fips is True.
    - response (dict): The response containing the census block data if only_block_fips is False.
    """
    # Calculate the center of the region
    if isinstance(coordinates, dict):
        SW = coordinates['SW']
        NE = coordinates['NE']
        center = [(SW[0] + NE[0]) / 2, (SW[1] + NE[1]) / 2]
    else:
        center = coordinates
        
    # Construct the API URL
    base_url= "https://geo.fcc.gov/api/census/block/find"
    params = {"lat":center[0],"lon":center[1],"censusYear":censusYear,"format":"json"}

    # Make the API request
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    
    # Return the block FIPS code or the entire response
    if only_block_fips:
        census_block_fips = response.json()['results'][0]['block_fips']
        return census_block_fips
    else:
        return response.json()



def get_census_data_for_block(census_block_fips,api_key, year=2020):
    """
    Retrieves census data for a specific census block.
    Parameters:
    - census_block_fips (str): The FIPS code of the census block.
    - api_key (str): The API key for accessing the census data.
    - year (int): The year for which the census data is requested. Default is 2020.
    Returns:
    - df (pandas.DataFrame): A DataFrame containing the retrieved census data.
    Raises:
    - Exception: If an error occurs during the retrieval of census data.
    """
    variable_dict = {
            "B19013_001E": "Median Household Income",
            "B19301_001E": "Per Capita Income",
            "B17021_002E": "Population Below Poverty Level",
            "B17021_001E": "Total Population for Poverty",
            "B23025_005E": "Unemployed Population",
            "B23025_002E": "Labor Force Population",
            "B15003_017E": "High School Graduate",
            "B15003_022E": "Bachelor's Degree or Higher",
            "B25077_001E": "Median Home Value",
            "B25064_001E": "Median Gross Rent",
            "B25003_002E": "Owner Occupied Housing Units",
            "B25003_001E": "Total Housing Units",
            "B02001_002E": "White Population",
            "B02001_003E": "Black or African American Population",
            "B03003_003E": "Hispanic or Latino Population",
            "B01002_001E": "Median Age",
            "B16001_002E": "Non-English Speakers",
            "B08301_010E": "Public Transit Commuters",
            "B08301_001E": "Total Commuters",
            "B25044_003E": "Households with No Vehicle",
            "B25044_001E": "Total Households"
        }
    from census import Census
    # Separate the FIPS code into its components
    state_fips = census_block_fips[:2]
    county_fips = census_block_fips[2:5]
    tract_code = census_block_fips[5:11]
    print(f"{state_fips=}, {county_fips=}, {tract_code=}")
    
    # Census api package from below 
    c = Census(api_key, year=year)
    results = c.acs5.get(('NAME', ",".join(variable_dict.keys())),
            geo = {'for': f"tract:{tract_code}",
                "in" :f'state:{state_fips} county:{county_fips}'})
    
    try:
        df = pd.DataFrame.from_records(results)
        df = df.rename(columns=variable_dict)
        # Calculate derived variables
        df['Poverty Rate'] = df['Population Below Poverty Level'].astype(float) / df['Total Population for Poverty'].astype(float) * 100
        df['Unemployment Rate'] = df['Unemployed Population'].astype(float) / df['Labor Force Population'].astype(float) * 100
        df['Percentage Owner Occupied'] = df['Owner Occupied Housing Units'].astype(float) / df['Total Housing Units'].astype(float) * 100
        df['Percentage Public Transit'] = df['Public Transit Commuters'].astype(float) / df['Total Commuters'].astype(float) * 100
        df['Percentage No Vehicle'] = df['Households with No Vehicle'].astype(float) / df['Total Households'].astype(float) * 100
        return df
    except Exception as e:
        display(e)
        return results
    