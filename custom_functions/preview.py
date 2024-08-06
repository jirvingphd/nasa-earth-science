import plotly.express as px 
import pandas as pd


# Visualization Functions
def generate_sample_points(sw, ne, num_points=10):
    """Generate sample points within a given bounding box."""
    latitudes = [sw[0] + i * (ne[0] - sw[0]) / (num_points - 1) for i in range(num_points)]
    longitudes = [sw[1] + i * (ne[1] - sw[1]) / (num_points - 1) for i in range(num_points)]
    return [(lat, lon) for lat in latitudes for lon in longitudes]


def preview_regions(data_params):
    """
    Generate a preview of selected bounding boxes for a given city region.
    Parameters:
    - data_params (dict): A dictionary containing the following keys:
        - 'coordinates' (dict): A dictionary containing region names as keys and bounding boxes as values.
            Each bounding box is represented by a dictionary with 'SW' and 'NE' keys, representing the
            southwest and northeast coordinates respectively.
        - 'city_region_name' (str): The name of the city region.
    Returns:
    - fig (plotly.graph_objects.Figure): A scatter mapbox plot showing the preview of selected bounding boxes.
    """
    # Dataframe to store results
    sampled_coordinates = []

    # Check if any coordinates within the bounding boxes are over sea
    for region, bounding_box in data_params['coordinates'].items():
        # Generate sample points within the bounding box
        sample_points = generate_sample_points(bounding_box['SW'], bounding_box['NE'], num_points=10)
        for lat, lon in sample_points:
            sampled_coordinates.append({'Region': region, 'Latitude': lat, 'Longitude': lon})

    # Convert results to DataFrame
    coords_df = pd.DataFrame(sampled_coordinates)
    
    ## Plot the region suggested
    fig = px.scatter_mapbox(coords_df, lat="Latitude", lon="Longitude", color='Region',
                            # color_continuous_scale="Viridis", 
                            mapbox_style="carto-positron",
                            title=f"Preview of Selected Bounding Boxes for {data_params['city_region_name']}",
                            height=600, width=600)

    # Remove left and right side margins
    fig.update_layout(
        margin={"r":0, "l":0,'b':0, 't':100},
        legend={'orientation':"h", 'yanchor':"top", 'y':1.05, 'xanchor':"left", 'x':0},
        
    )
    return fig
