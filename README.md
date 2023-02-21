# Map

## About map
In this laboratory work, we made a map of films, by their locations.
This map has three layers:
1) main map
2) layer of nearest film from my location by year
3) layer of all films by year

### How to run map?
<img src="https://github.com/yarynas21/map/blob/main/launch.png" alt="my image" width="500">
First attribute after name of file is "Yaer" (2000)
Second attribute is "Latitude" (49.83826)
Third attribute is "Longitude" (24.02324)
Fourth attribute is "Path_to_dataset" (Users/yarynasavkiv/Desktop/maapp/locations.list)

##Visualisation

Main map with all three layers:
<img src="https://github.com/yarynas21/map/blob/main/alll.png" alt="my image" width="4444">

Map with nearest films:
<img src="https://github.com/yarynas21/map/blob/main/closest.png" alt="my image" width="500">
if distance is more than 600 km circle is red, in other case circle is yellow.

Map with all films by year:
<img src="https://github.com/yarynas21/map/blob/main/films.png" alt="my image" width="500">
My code has limits to read main file, if you want to change it, you can do this by changing limit in function read_file.
Also, I wrote doctests on a shorter file.
