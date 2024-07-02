import xml.etree.ElementTree as ET
import pandas as pd

def xml_to_dict(element):
    """
    Converts an XML element to a dictionary.

    Args:
        element (Element): The XML element to convert.

    Returns:
        dict: The converted dictionary representation of the XML element.
    """
    import xml.etree.ElementTree as ET
    # If the element has no children, return its text
    if not list(element):
        return element.text
    
    # If the element has children, create a dictionary
    child_dict = {}
    for child in element:
        child_tag = child.tag
        child_dict.setdefault(child_tag, [])
        child_dict[child_tag].append(xml_to_dict(child))
    
    # Simplify lists with single elements
    for key in child_dict:
        if len(child_dict[key]) == 1:
            child_dict[key] = child_dict[key][0]
    
    return child_dict


def extract_coordinates(raw_xml_data=None, xml_file_path=None):
    """
    Extracts coordinates from XML data or file.

    Args:
        raw_xml_data (str): The raw XML data as a string. Default is None.
        xml_file_path (str): The path to the XML file. Default is None.

    Returns:
        list: A list of tuples containing latitude and longitude coordinates.

    Raises:
        FileNotFoundError: If the XML file is not found.

    """
    if (raw_xml_data is None) and (xml_file_path is not None):
        with open(xml_file_path) as f:
            raw_xml_data = f.read()
    
    # Parse the XML content
    root = ET.fromstring(raw_xml_data)

    coordinates = []
    for point in root.findall(".//Point"):
        lon = float(point.find('PointLongitude').text)
        lat = float(point.find('PointLatitude').text)
        coordinates.append((lat, lon))
    return coordinates


# Label coordinates
def label_coordinates(coordinates):
    """
    Sorts a list of coordinates and returns a dictionary of labeled coordinates.

    Args:
        coordinates (list): A list of coordinate tuples in the format (latitude, longitude).

    Returns:
        dict: A dictionary containing labeled coordinates in the format {"SW": (latitude, longitude), "SE": (latitude, longitude), "NW": (latitude, longitude), "NE": (latitude, longitude)}.

    """
    coordinates.sort()  # Sort by latitude first (south to north)
    
    # Determine the south and north points
    south_points = coordinates[:2]
    north_points = coordinates[2:]

    # Sort by longitude (west to east) within the south and north points
    south_points.sort(key=lambda x: x[1])
    north_points.sort(key=lambda x: x[1])

    labels = {
        "SW": south_points[0],
        "SE": south_points[1],
        "NW": north_points[0],
        "NE": north_points[1]
    }
    return labels



def preview_xml_dict(xml_dict):
    """
    Preview the structure of a nested XML dictionary.

    Args:
        xml_dict (dict): The XML dictionary to preview.

    Returns:
        None
    """
    # Preview nested dictionary
    print("XML Dict Structure:")
    for k,v in xml_dict.items():
        print(f"- {k} (type={type(v)})")
        if isinstance(v,str):
            print(f"\t{v}")
        elif isinstance(v,dict):
            for kk,vv in v.items():
                print(f"\t- {kk} (type={type(vv)})")
                if isinstance(vv,str):
                    print(f"\t\t{vv}")
                elif isinstance(vv,dict):
                    print(f"\t\t{vv}")
                elif isinstance(vv,list):
                    for i in vv:
                        print(f"\t\t{i}")
        elif isinstance(v,list):
            for i in v:
                print(f"\t- {i}")
                
                
                
                

def clean_xml_dict(xml_dict, top_keys_strings=['GranuleUR', 'InsertTime', 'LastUpdate', 'DataFormat'],
                   top_keys_simple_dicts=['Collection', 'PGEVersionClass'],
                   top_keys_nested_dicts=['DataGranule', 'Temporal', 'Campaigns'],
                   spatial_key='Spatial', addl_attributes_key="AdditionalAttributes"):
    """
    Cleans and flattens a nested XML dictionary to retain only relevant keys and values.

    This function processes an XML dictionary by retaining specified top-level string keys,
    flattening nested dictionaries, and converting lists within the nested dictionaries to DataFrames.
    It filters out undesired keys, such as those related to 'AdditionalFile'.

    Parameters:
    xml_dict (dict): The input XML dictionary to be cleaned and flattened.
    top_keys_strings (list): A list of keys corresponding to top-level strings to retain in the output dictionary.
    top_keys_simple_dicts (list): A list of keys corresponding to simple nested dictionaries to flatten and retain.
    top_keys_nested_dicts (list): A list of keys corresponding to nested dictionaries to process and flatten.
    spatial_key (str): The key corresponding to spatial data in the input dictionary.

    Returns:
    dict: A cleaned and flattened dictionary containing only the relevant keys and values.

    Example:
    >>> xml_dict = {
            'GranuleUR': 'MOD11A2.A2024153.h09v06.061.2024162202838',
            'InsertTime': '2024-06-10T17:04:37.341Z',
            'LastUpdate': '2024-06-10T17:05:14.132Z',
            'Collection': {'ShortName': 'MOD11A2', 'VersionId': '061'},
            'DataGranule': {'SizeMBDataGranule': 3.156, 'DayNightFlag': 'BOTH'},
            'AdditionalFile': [{'Name': 'file1', 'SizeInBytes': 100}, {'Name': 'file2', 'SizeInBytes': 200}],
            'Temporal': {'RangeDateTime': {'BeginningDateTime': '2024-06-01T00:00:00Z', 'EndingDateTime': '2024-06-08T23:59:59Z'}},
            'Spatial': {'HorizontalSpatialDomain': {'Geometry': {'GPolygon': {'Boundary': {'Point': [{'PointLongitude': -103.923, 'PointLatitude': 30}, {'PointLongitude': -92.0525, 'PointLatitude': 30.0438}]}}}}},
            'PGEVersionClass': {'PGEVersion': '6.4.4'}
        }
    >>> clean_xml_dict(xml_dict)
    {
        'GranuleUR': 'MOD11A2.A2024153.h09v06.061.2024162202838',
        'InsertTime': '2024-06-10T17:04:37.341Z',
        'LastUpdate': '2024-06-10T17:05:14.132Z',
        'DataFormat': 'HDF-EOS2',
        'Collection__ShortName': 'MOD11A2',
        'Collection__VersionId': '061',
        'DataGranule__SizeMBDataGranule': 3.156,
        'DataGranule__DayNightFlag': 'BOTH',
        'Temporal__RangeDateTime__BeginningDateTime': '2024-06-01T00:00:00Z',
        'Temporal__RangeDateTime__EndingDateTime': '2024-06-08T23:59:59Z',
        'PGEVersionClass__PGEVersion': '6.4.4'
    }
    """
    # Initialize dictionary to keep only the relevant keys
    keep_xml = {}

    # Save top level keys
    for k in top_keys_strings:
        if k in xml_dict.keys():
            keep_xml[k] = xml_dict[k]

    # Save simple nested keys
    for k in top_keys_simple_dicts:
        if k in xml_dict.keys():
            # If single key, combine with parent key        
            for kk, vv in xml_dict[k].items():
                keep_xml[f"{k}__{kk}"] = vv

    # Save nested dictionaries as flat keys            
    for k in top_keys_nested_dicts:
        if k in xml_dict.keys():
            # Combine parent key and child key to flat key
            for kk, vv in xml_dict[k].items():
                # Skip undesired keys:
                if 'AdditionalFile'.lower() in kk.lower():
                    continue

                if isinstance(vv, list):
                    vv = pd.DataFrame(vv)
                    keep_xml[f"{k}__{kk}"] = vv

                elif isinstance(vv, dict):
                    # Combine parent key and child key to flat key
                    for kkk, vvv in vv.items():
                        key = f"{k}__{kk}__{kkk}"
                        keep_xml[key] = vvv
                else:
                    key = f"{k}__{kk}"
                    keep_xml[key] = vv

    ## Save addiitonal attirubtes
    additional_attributes = xml_dict[addl_attributes_key]['AdditionalAttribute']
    for li in additional_attributes:
        # print(li)
        key = f"AddlAttr__{li['Name']}"
        
        if isinstance(li['Values'], dict):
            keep_xml[key] = li['Values']['Value']
        else:
            keep_xml[key] = li["Values"]
    return keep_xml



def parse_and_clean_xml_file(xml_file_path, labeled_coordinates=True, as_series=False):
    """
    Extracts and completes the XML data from the specified file path.

    Args:
        xml_file_path (str): The file path of the XML file.

    Returns:
        dict: A dictionary containing the completed XML data, with column names as keys and values as values.
    """
    # Extract the cleaned XML data
    # Parse the XML data
    with open(xml_file_path) as f:
        xml_data = f.read()
        
        
    # Parse the XML data
    root = ET.fromstring(xml_data)

    # Convert the XML to a dictionary
    xml_dict = xml_to_dict(root)

    xml_dict_clean = clean_xml_dict(xml_dict)
    
    # Extract the coordinates
    coordinates = extract_coordinates(raw_xml_data=xml_data)#xml_file_path=xml_file_path)
    
    if labeled_coordinates:
        # Label the coordinates
        coordinates = label_coordinates(coordinates)
    
    # Combine the cleaned XML data and coordinates
        for k,v in coordinates.items():
            xml_dict_clean[f"Spatial_Coordinates__{k}"] = v

    
    if as_series:
        return pd.Series(xml_dict_clean)
    return xml_dict_clean
