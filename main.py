"""MAPA"""
from functools import lru_cache
import pandas as pd
import argparse
import folium
from folium import plugins
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import math

parser = argparse.ArgumentParser()
parser.add_argument("Year", help='print year')
parser.add_argument("Latitude", help='print latitude')
parser.add_argument("Longitude", help='print longitude')
parser.add_argument("Path_to_dataset", help='print path_to_dataset')
args = parser.parse_args()

geolocator = Nominatim(user_agent="my_html")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds= 1)

def read_file(file_name: list) -> list:
    """
    This function is to read file.
    >>> read_file("locations_sh.list")
    ['"#1 Single" (2006) Los Angeles, California, USA', '"#1 Single" (2006) New York City, New York, USA', \
'"#15SecondScare" (2015)  Coventry, West Midlands, England, UK', '"#15SecondScare" (2015)  West Hills, California, USA', \
'"#15SecondScare" (2015)  West Hills, California, USA', '"#2WheelzNHeelz" (2017) Nashville, Tennessee, USA']
    """
    with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
        my_list = []
        for i, line in enumerate(file):
            if i >= 2000:
                break
            my_list.append(line.strip())
    new = my_list[14:]
    temp = []
    for item in new:
        parts = item.split('\t')
        # print(parts)
        if parts[-1].startswith("("):
            parts = parts[:-1]
        title_year = parts[0]
        location = [parts[-1]]
        res = ",".join(location)
        temp += [title_year + " " + res]
    res = []
    for elem in temp:
        if "{" in elem:
            elem1 = elem[:elem.find('{')]
            elem2 = elem[elem.find('}') + 1:]
            elem = elem1 + elem2
        res.append(elem)
    return res

@lru_cache(maxsize=None)
def get_location(name: str):
    """
    Get coordinates from location of city.
    >>> get_location('New York City, New York, USA')
    Location(City of New York, New York, United States, (40.7127281, -74.0060152, 0.0))
    """
    return geolocator.geocode(name)

def haversine(latitude1, longitude1, latitude2, longitude2):
    """
    This function to search length between to coordinates.
    >>> haversine(49.83826, 24.02324, 52.505003, -1.964396)
    1825.64
    """
    earth_radius = 6371
    d_lat = math.radians(latitude2 - latitude1)
    d_lon = math.radians(longitude2 - longitude1)
    lat1 = math.radians(latitude1)
    lat2 = math.radians(latitude2)
    alls = math.sin(d_lat/2) * math.sin(d_lat/2) + math.sin(d_lon/2) * math.sin(d_lon/2) * math.cos(lat1) * math.cos(lat2)
    cin = 2 * math.atan2(math.sqrt(alls), math.sqrt(1 - alls))
    distance = earth_radius * cin
    return round(distance, 2)
# print(haversine(49.83826, 24.02324, 52.505003, -1.964396))

def create_table(file_name):
    """
    Create table of all data.
    >>> create_table("locations_sh.list")
                    Name  Year                      Location   Latitude   Longitude     Distance
    2  "#15SecondScare"   2015    West Midlands, England, UK  52.505003   -1.964396  1825.644221
    3  "#15SecondScare"   2015   West Hills, California, USA  34.203232 -118.645476  9972.749610
    4  "#15SecondScare"   2015   West Hills, California, USA  34.203232 -118.645476  9972.749610
    """
    information = read_file(file_name)
    names = [elem[0 : elem.find('(')] for elem in information if '"' in elem]
    years = [eli[eli.find('(') + 1 : eli.find(')')] for eli in information]
    res = [els[els.find(')') + 2:] for els in information]
    locations = []
    for elem in res:
        elem = elem.split(",")
        if len(elem) > 3:
            elem = elem[1:]
        locations.append(",".join(elem))
    df = pd.DataFrame({"Name": names, "Year": years, "Location": locations})
    df = df.loc[df['Year'] == args.Year]
    location = list(df.loc[:, 'Location'])
    # визначаю координати
    latitude = []
    longitude = []
    for point in location:
        try:
            location = get_location(point)
            latitude.append(location.latitude)
            longitude.append(location.longitude)
        except AttributeError:
            latitude.append(None)
            longitude.append(None)
    df["Latitude"] = latitude
    df["Longitude"] = longitude
    df = df.dropna(subset=["Latitude", "Longitude"])
    # шукаємо відстань від найближче заданих координат
    user_lat = args.Latitude
    user_lon = args.Longitude
    to_f_lat = list(df.loc[:, 'Latitude'])
    to_f_lon = list(df.loc[:, 'Longitude'])
    df["Distance"] = [haversine(float(user_lat), float(user_lon), float(lt), float(ln)) for lt, ln in zip(to_f_lat, to_f_lon)]
    return df
# print(create_table("locations.list"))

def create_mapa(file_name):
    """
    Function to create mapa by folium.
    """
    df = create_table(file_name)
    lati = list(df.loc[:,'Latitude'])
    longi = list(df.loc[:,'Longitude'])
    nami = list(df.loc[:,'Name'])
    # найближчі 10 точок
    closest_points = df.nsmallest(10, 'Distance')
    closest_latitude = list(closest_points['Latitude'])
    closest_longitude = list(closest_points['Longitude'])
    names = list(closest_points['Name'])

    map = folium.Map(tiles="Stamen Terrain",
                location=[args.Latitude, args.Longitude],
                zoom_start=5)
    map.add_child(folium.Marker(location=[args.Latitude, args.Longitude],
                            popup="That's your location!",
                            icon=folium.Icon()))
    fg_k = folium.FeatureGroup(name="Names of closest films")
    fg_all = folium.FeatureGroup(name = f"Names of all films {args.Year}")
    for clt, cln, nn, dist in zip(closest_latitude, closest_longitude, names, closest_points['Distance']):
        if dist > 600:
            color = 'red'
        else:
            color = 'orange'
        fg_k.add_child(folium.CircleMarker(location=[clt, cln],
                                            radius=10,
                                            popup= nn,
                                            color=color,
                                            fill_opacity=0.5))
    for lt, ln, nm in zip(lati, longi, nami):
        fg_all.add_child(folium.Marker(location=[lt,ln],
                            popup=nm,
                            icon=folium.Icon(color = "pink")))
    map.add_child(plugins.MiniMap())
    map.add_child(plugins.Terminator())
    map.add_child(fg_k)
    map.add_child(fg_all)
    map.add_child(folium.LayerControl())
    map.save('Map_Kinos.html')

if __name__ == "__main__":
    create_mapa(args.Path_to_dataset)
    print("READY!!!")
    # import doctest
    # print(doctest.testmod())
