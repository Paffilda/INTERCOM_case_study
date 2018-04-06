import json
import math

# variables
file_path = 'customers.txt'
outfile_path = 'customers_outfile.txt'
max_distance_km = 100
lat_office = 53.339428
lon_office = -6.257664

# constants
radian_degree_const = 57.2957795
equatorial_radius = 6378.137
polar_radius = 6356.7523


def read_file(filepath):
    """
    :param filepath: path to file with customers data
    :return: list of json objects with customers data
    """
    list_of_jsons = []
    with open(filepath, 'r') as infile:
        for rowidx, row in enumerate(infile):
            try:
                json_row = json.loads(row)

                # check if there are all necessary values, otherwise raise KeyError
                try:
                    json_row["user_id"] and json_row["latitude"] and json_row["longitude"] and json_row["name"]
                except KeyError:
                    raise KeyError("there are missing required values on line number {rownum}".format(
                        rownum=rowidx + 1))

                # check if primary key user_id is not null, otherwise raise error
                if json_row["user_id"] is None:
                    raise Exception("user_id is missing on line number {rownum}".format(
                        rownum=rowidx+1))

                # check if lat values are within valid range
                if float(json_row["latitude"]) < -180 or float(json_row["latitude"]) > 180:
                    raise Exception("latitude is not a valid value in degrees on line number {rownum}".format(
                        rownum=rowidx+1))

                # check if lon values are within valid range
                if float(json_row["longitude"]) < -90 or float(json_row["longitude"]) > 90:
                    raise Exception("longitude is not a valid value in degrees on line number {rownum}".format(
                        rownum=rowidx + 1))

                list_of_jsons.append(json_row)

            except json.decoder.JSONDecodeError:
                print("JSON not valid on line number {rownum}".format(
                    rownum=rowidx+1))

    return list_of_jsons


def earth_radius_lat(lat):
    """
    :param lat: latitude in degrees
    :return: float, Earth radius at specified latitude
    """
    numerator = ((equatorial_radius ** 2 * math.cos(lat)) ** 2)
    denominator = ((equatorial_radius * math.cos(lat)) ** 2 + (polar_radius * math.sin(lat)) ** 2)

    return math.sqrt(numerator/denominator)


def distance(lat, lon, lat_center=lat_office, lon_center=lon_office):
    """
    :param lat: customer latitude in degrees
    :param lon: customer longitude in degrees
    :param lat_center: latitude of the office in degrees
    :param lon_center: longitude of the office in degrees
    :return: float, distance of cutomer from the office in km
    """
    lat_rad = lat/radian_degree_const
    lon_rad = lon/radian_degree_const
    lat_center_rad = lat_center/radian_degree_const
    lon_center_rad = lon_center/radian_degree_const
    x = math.sin(lat_rad) * math.sin(lat_center_rad)
    y = math.cos(lat_rad) * math.cos(lat_center_rad) * math.cos(lon_center_rad-lon_rad)

    return earth_radius_lat(lat_center)*math.acos(x+y)


indata = read_file(file_path)
outdata = []

for d in indata:
    lon = float(d["longitude"])
    lat = float(d["latitude"])
    if distance(lat, lon) <= max_distance_km:

        outdata.append(d)

outdata_sorted = sorted(outdata, key=lambda i: int(i["user_id"]))

# clear contents of outfile if exists
open(outfile_path, 'w').close()

# write data to outfile
with open(outfile_path, 'a') as outfile:
    outfile.truncate()
    for item in outdata_sorted:
        json.dump(item, outfile)
        outfile.write('\n')
