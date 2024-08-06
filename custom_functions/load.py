import xarray as xr
from pyproj import Proj, transform
import xarray as xr
import rioxarray
import numpy as np
import pyproj
from pyproj import Transformer, CRS
import re

def convert_temp_in_array(dataset, verbose=True):
    """
    Converts the Land Surface Temperature (LST) values in the dataset from Kelvin to Celsius and Fahrenheit.
    Args:
        dataset (xarray.Dataset): The dataset containing the LST values.
        verbose (bool, optional): If True, prints the updated dataset. Defaults to True.
    Returns:
        xarray.Dataset: The dataset with the LST values converted to Celsius and Fahrenheit.
    """
    
    # Convert LST from Kelvin to Celsius
    lst_celsius = dataset['LST_Day_1km']-273.15#* 0.02 - 273.15

    # Convert LST from Celsius to Fahrenheit
    lst_fahrenheit = (lst_celsius * 9 / 5) + 32

    # Add these new variables to the dataset
    dataset['LST_Day_1km_C'] = lst_celsius #(('time', 'YDim:MODIS_Grid_8Day_1km_LST', 'XDim:MODIS_Grid_8Day_1km_LST'), lst_celsius.data)
    # Add attributes to the new variables
    dataset['LST_Day_1km_C'].attrs['units'] = 'Celsius'
    dataset['LST_Day_1km_C'].attrs['description'] = 'Land Surface Temperature in Celsius'


    # Add these new variables to the dataset
    dataset['LST_Day_1km_F'] = lst_fahrenheit #(('time', 'YDim:MODIS_Grid_8Day_1km_LST', 'XDim:MODIS_Grid_8Day_1km_LST'), lst_fahrenheit.data)
    # Add attributes to the new variables
    dataset['LST_Day_1km_F'].attrs['units'] = 'Fahrenheit'
    dataset['LST_Day_1km_F'].attrs['description'] = 'Land Surface Temperature in Fahrenheit'

    if verbose:
        # Inspect the updated dataset
        print("Updated Dataset:\n", dataset)

    return dataset


def save_coordinates(ds, verbose=True):
    """
    Save the coordinates of a dataset.
    Parameters:
    - ds (xarray.Dataset): The dataset containing the data.
    - verbose (bool): Whether to print additional information. Default is True.
    Returns:
    - xarray.Dataset: The dataset with added latitude and longitude coordinates.
    """
    # Rest of the code...
    # Step 2: Parse the StructMetadata.0 attribute
    metadata = ds.attrs['StructMetadata.0']

    # Extract relevant information using regex
    upper_left = re.search(r'UpperLeftPointMtrs=\((.*?)\)', metadata).group(1).split(',')
    lower_right = re.search(r'LowerRightMtrs=\((.*?)\)', metadata).group(1).split(',')
    dims = re.search(r'XDim=(\d+)\s+YDim=(\d+)', metadata)#.group(1)
    if verbose:
        print(f"{upper_left=}, {lower_right=}, {dims=}")

    upper_left_x, upper_left_y = map(float, upper_left)
    lower_right_x, lower_right_y = map(float, lower_right)
    x_dim, y_dim = map(int, dims.groups())

    # Step 3: Define the projection
    proj_params_match = re.search(r'ProjParams=\((.*?)\)', ds.attrs['StructMetadata.0'])
    proj_params_str = proj_params_match.group(1)
    proj_params = list(map(float, proj_params_str.split(',')))
    modis_sinu_regex = Proj(proj='sinu', R=proj_params[0], x_0=proj_params[8])
    if verbose:
        print(modis_sinu_regex.definition)
        
    # Step 3: Set up projections
    modis_sinu = CRS.from_string(modis_sinu_regex.definition)#'+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m')
    if verbose:
        print(modis_sinu_regex.definition)
    wgs84 = CRS.from_epsg(4326)

    # Step 4: Create coordinate arrays
    x = np.linspace(upper_left_x, lower_right_x, x_dim)
    y = np.linspace(upper_left_y, lower_right_y, y_dim)

    
    # Step 5: Create a mesh grid of coordinates
    xx, yy = np.meshgrid(x, y)

    # Step 6: Transform coordinates to lat/lon
    transformer = Transformer.from_crs(modis_sinu, wgs84, always_xy=True)
    lons, lats = transformer.transform(xx, yy)

    if verbose:
        print(f"Longitude range: {lons.min()} to {lons.max()}")
        print(f"Latitude range: {lats.min()} to {lats.max()}")

    # Step 8: Add rounded lat/lon coordinates to the dataset
    ds = ds.assign_coords(lon=(('YDim:MODIS_Grid_8Day_1km_LST', 'XDim:MODIS_Grid_8Day_1km_LST'), lons),
                        lat=(('YDim:MODIS_Grid_8Day_1km_LST', 'XDim:MODIS_Grid_8Day_1km_LST'), lats))

    return ds


def slice_coordinates(ds, sw_lat=None, sw_lon=None, ne_lat=None, ne_lon=None,
                                            data_params=None, region_name=None, tolerance=0.05, verbose=True):
    """
    Slice a dataset based on the given bounding box coordinates or region name.
    Parameters:
        - ds (xarray.Dataset): The dataset to be sliced.
        - sw_lat (float, optional): The latitude of the southwest corner of the bounding box. Default is None.
        - sw_lon (float, optional): The longitude of the southwest corner of the bounding box. Default is None.
        - ne_lat (float, optional): The latitude of the northeast corner of the bounding box. Default is None.
        - ne_lon (float, optional): The longitude of the northeast corner of the bounding box. Default is None.
        - data_params (dict, optional): A dictionary containing the bounding box coordinates for different regions. Default is None.
        - region_name (str, optional): The name of the region to be sliced. Required if data_params is provided. Default is None.
        - tolerance (float, optional): The tolerance value for expanding the bounding box. Default is 0.05.
        - verbose (bool, optional): Whether to print verbose output. Default is True.
    Returns:
        - sliced_ds (xarray.Dataset): The sliced dataset based on the given bounding box or region.
    Raises:
        - ValueError: If neither the bounding box coordinates nor the data_params dictionary is provided.
        - ValueError: If the region name is not provided when data_params is provided.
    """
    
    
    if (sw_lat is None) or (sw_lon is None) or (ne_lat is None) or (ne_lon is None):
        if data_params is None:
            raise ValueError("Please provide either the bounding box coordinates or the data_params dictionary.")
        if region_name is None:
            raise ValueError("Please provide the region name from the data_params dictionary.")
        
        # Define your bounding box (SW and NE corners)
        sw_lat, sw_lon = data_params['coordinates'][region_name]['SW']
        ne_lat, ne_lon = data_params['coordinates'][region_name]['NE']

    # Create a boolean mask for the bounding box
    mask = (
        (ds.lat >= sw_lat-tolerance) & 
        (ds.lat <= ne_lat+tolerance) & 
        (ds.lon >= sw_lon-tolerance) & 
        (ds.lon <= ne_lon+tolerance)
    )
    
    if verbose:
        print(f"{sw_lat-tolerance=}, {ne_lat+tolerance=}, {sw_lon-tolerance=}, {ne_lon+tolerance=}")
        print(mask.sum().item())
        
    # Apply the mask to slice the dataset
    sliced_ds = ds.where(mask, drop=True)

    return sliced_ds


def extract_times_from_metadata(ds, as_dim=False):
    """
    Extracts the start and end times from the metadata of a dataset.
    Parameters:
    - ds: xarray.Dataset
        The dataset containing the metadata.
    - as_dim: bool, optional
        If True, the dataset will be expanded with the start time as a new dimension.
    Returns:
    - ds: xarray.Dataset
        The dataset with the start and end times added as attributes.
        If as_dim is True, the dataset will also have the start time as a new dimension.
    """
    import re
    from datetime import datetime

    core_metadata = ds.attrs['CoreMetadata.0']
    # Regular expressions to extract date and time
    start_date_pattern = re.compile(r'RANGEBEGINNINGDATE.*?VALUE\s+=\s"(.*?)"', re.DOTALL)
    start_time_pattern = re.compile(r'RANGEBEGINNINGTIME.*?VALUE\s+=\s+"(.*?)"', re.DOTALL)

    # Extract dates and times
    beginning_date = start_date_pattern.search(core_metadata).group(1)# Group 1 is first match, 0 is full string
    beginning_time = start_time_pattern.search(core_metadata).group(1) 

    # Convert to datetime
    beginning_datetime = datetime.strptime(f"{beginning_date} {beginning_time}", "%Y-%m-%d %H:%M:%S")

    # Repeat process for ending date/time
    end_date_pattern = re.compile(r'RANGEENDINGDATE.*?VALUE\s+=\s+"(.*?)"', re.DOTALL)
    end_time_pattern = re.compile(r'RANGEENDINGTIME.*?VALUE\s+=\s+"(.*?)"', re.DOTALL)

    # Extract dates and times
    ending_date = end_date_pattern.search(core_metadata).group(1)#1
    ending_time = end_time_pattern.search(core_metadata).group(1)#1

    # Convert to datetime
    ending_datetime = datetime.strptime(f"{ending_date} {ending_time}", "%Y-%m-%d %H:%M:%S")
    
    ### TO DO: Try adding as attrs first
    ## Adding the start and end time as coordinates to the dataset
    ds.attrs['start_time'] = beginning_datetime
    ds.attrs['end_time'] = ending_datetime
    
    if as_dim:
        ds = ds.expand_dims({"start_time":[beginning_datetime]})
    return ds



def load_data(hdf_fname, data_params, region_name, time_as_dim=False, slice=False,slice_tolerance=.05, verbose=True):
    """
    Load data from an HDF file and perform various data processing steps.
    Parameters:
    - hdf_fname (str): The file path of the HDF file.
    - data_params (dict): A dictionary containing data parameters.
    - region_name (str): The name of the region.
    - time_as_dim (bool): Whether to treat time as a dimension (default: False).
    - slice (bool): Whether to slice the data based on coordinates (default: False).
    - slice_tolerance (float): The tolerance for slicing coordinates (default: 0.05).
    - verbose (bool): Whether to display verbose output (default: True).
    Returns:
    - x_data (xarray.Dataset): The processed dataset.
    """
    
    # Open the dataset
    x_data = xr.open_dataset(hdf_fname, engine='netcdf4')

    
    ## Convert the temperature from Kelvin to Celsius and Fahrenheit
    x_data = convert_temp_in_array(x_data, verbose=verbose)
    
    # Save the coordinates from data params
    coordinate_dict = data_params['coordinates'][region_name]
    sw_lat,sw_lon = coordinate_dict['SW']
    ne_lat,ne_lon = coordinate_dict['NE']
    
    # x_data = save_coordinates(x_data, lat1, lat2, lon1, lon2)
    x_data = save_coordinates(x_data, 
                              #data_params, region_name, 
                              verbose=verbose)

    # Save the group name
    x_data = x_data.expand_dims(region=[region_name])
    
    ## TO DO: Decide if time should be saved as a coordinate or attribute
    # Add time as a coords
    x_data = extract_times_from_metadata(x_data,as_dim=time_as_dim)
    
    if slice:
        x_data = slice_coordinates(x_data, sw_lat=sw_lat, sw_lon=sw_lon, ne_lat=ne_lat, ne_lon=ne_lon,
                                #    data_params, region_name, 
                                   tolerance=slice_tolerance, verbose=verbose)
    return x_data
    duplicate_arrays.append(x_data)
    