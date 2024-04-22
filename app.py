import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# load data
def load_data(csv):
    df = pd.read_csv(csv)
    return df

st.header('House Campaign Finances')

df = pd.read_csv('data/house_finances.csv')
st.button('hello')
st.dataframe(df)

# filter data for only elected candidates
state_data = df[df["Win?"] == 1]

# group by state and party group
state_party_counts = state_data.groupby(['State', 'Party Group']).size().unstack(fill_value=0)

# determine what the controlling party for each state is
for index, row in state_party_counts.iterrows():
    if row['Republican Party'] > row['Democratic Party']:
        state_party_counts.at[index, 'Controlling Party'] = 'Republican Party'
    elif row['Democratic Party'] > row['Republican Party']:
        state_party_counts.at[index, 'Controlling Party'] = 'Democratic Party'
    else:
        state_party_counts.at[index, 'Controlling Party'] = 'Tieds'

# change state index to column and rename to match shapefile
state_party_counts.index.name = "NAME"
state_party_counts.reset_index(inplace=True)

# drop territories
state_party_counts = state_party_counts.drop(2)
state_party_counts = state_party_counts.drop(12)
state_party_counts = state_party_counts.drop(37)

# load shapefile
my_USA_map = gpd.read_file('data/cb_2018_us_state_500k.shp')

# drop territories
my_USA_map = my_USA_map.drop(45)
my_USA_map = my_USA_map.drop(37)
my_USA_map = my_USA_map.drop(38)
my_USA_map = my_USA_map.drop(44)
my_USA_map = my_USA_map.drop(13)

#Select a party group
st.sidebar.title("Select Party Group: ")
group = st.sidebar.selectbox(
    'Party Group',
    ('Democratic Party', 'Republican Party', 'Third Party'))

st.write('You selected:', group)

#Naming Map
st.header('US States & Their Affiliated Parties')

# merge dataframe and geopandas dataframe
gdf = my_USA_map.merge(state_party_counts, on='NAME')

# make map
m = folium.Map(location=[37, -102], zoom_start=4)

# function to assign color based on party
def assign_color(party):
    if party == 'Republican Party':
        return 'red'
    elif party == 'Democratic Party':
        return 'blue'
    else:
        return 'gray'

# use function to make color column in dataframe
gdf['color'] = gdf['Controlling Party'].apply(assign_color)

geojson_data = gdf.to_json()

folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        'fillColor': feature['properties']['color'],
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(fields=['NAME', 'Controlling Party'],
                                  aliases=['State', 'Controlling Party'],
                                  localize=True)
).add_to(m)

folium_static(m)
