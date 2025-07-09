import os

import folium
import pandas as pd
from folium.plugins import MarkerCluster

from snowpylot.caaml_parser import caaml_parser

# Define the folder path for 2019-2020 season
folder_path = "demos/snowpits/by_season/2019-2020"

# Get a list of all CAAML files in the folder
caaml_files = [f for f in os.listdir(folder_path) if f.endswith(".xml")]

# Create lists to store latitude and longitude data
latitudes = []
longitudes = []
pit_ids = []
countries = []
regions = []

# Parse each CAAML file and extract location data
for file in caaml_files:
    file_path = os.path.join(folder_path, file)
    try:
        pit = caaml_parser(file_path)

        # Check if latitude and longitude are available
        if (
            pit.core_info.location.latitude is not None
            and pit.core_info.location.longitude is not None
        ):
            latitudes.append(pit.core_info.location.latitude)
            longitudes.append(pit.core_info.location.longitude)
            pit_ids.append(pit.core_info.pit_id)
            countries.append(pit.core_info.location.country)
            regions.append(pit.core_info.location.region)
    except Exception as e:
        print(f"Error parsing {file}: {e}")

# Create a DataFrame with the location data
df = pd.DataFrame(
    {
        "PitID": pit_ids,
        "Latitude": latitudes,
        "Longitude": longitudes,
        "Country": countries,
        "Region": regions,
    }
)

# Print summary statistics
print(f"Total snowpits with location data: {len(df)}")
print("\nTop 10 countries by number of snowpits:")
print(df["Country"].value_counts().head(10))

# Create a map centered on the mean latitude and longitude
center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=4)

# Create a marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Get unique countries
unique_countries = df["Country"].unique()

# Define colors for different countries
colors = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "lightred",
    "beige",
    "darkblue",
    "darkgreen",
    "cadetblue",
    "darkpurple",
    "pink",
    "lightblue",
    "lightgreen",
    "gray",
    "black",
    "lightgray",
]

# Create a dictionary mapping countries to colors
country_to_color = dict(zip(unique_countries, colors[: len(unique_countries)]))

# Add markers for each snowpit with country-specific colors
for _idx, row in df.iterrows():
    # Create a popup with information about the snowpit
    popup_text = f"""
    <b>Pit ID:</b> {row["PitID"]}<br>
    <b>Country:</b> {row["Country"]}<br>
    <b>Region:</b> {row["Region"]}<br>
    <b>Latitude:</b> {row["Latitude"]:.4f}<br>
    <b>Longitude:</b> {row["Longitude"]:.4f}
    """

    # Get the color for this country
    color = country_to_color.get(row["Country"], "red")

    # Add a marker to the cluster
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(marker_cluster)

# Add a title to the map
title_html = """
<div style="position: fixed;
            top: 10px; left: 50px; width: 300px; height: 30px;
            border:2px solid grey; z-index:9999;
            background-color:white;
            padding: 10px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;">
    Global Distribution of Snowpits by Country (2019-2020 Season)
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

# Add a legend
legend_html = """
<div style="position: fixed;
            bottom: 50px; right: 50px; width: 200px; height: 300px;
            border:2px solid grey; z-index:9999;
            background-color:white;
            padding: 10px;
            font-size: 14px;
            overflow-y: auto;">
    <h4>Countries</h4>
"""

for country, color in country_to_color.items():
    legend_html += f"""
    <div>
        <span style="color: {color}; font-weight: bold;">■</span> {country}
    </div>
    """

legend_html += "</div>"
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map
m.save("demos/snowpit_distribution_by_country_2019_2020.html")

print(
    "Map has been created and saved as 'demos/snowpit_distribution_by_country_2019_2020.html'"  # noqa: E501
)
print("Open the HTML file in a web browser to view the interactive map.")
