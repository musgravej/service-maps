import re
# import json
import configparser
# import os
import urllib3
import requests
import shutil


class Api:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.key = config['API']['key']


def only_numbers_in_list_elements(list_of_numbers):
    return list(map(lambda x: re.sub("\D", "", x), list_of_numbers))


def get_list_lat_lon(zip_list):
    """
    Returns a list of batch search responses for lat and lon by ZIP code
    :param zip_list: list of zip codes
    :return: list if dict responses {'location:zip, latlng: {lat:lat, lng:lng}}
    """
    api = Api().key
    zip_list = [str(z) for z in zip_list]
    location_list = "".join(list(map(lambda x:  '&location='+x+',US', zip_list)))
    url = "http://www.mapquestapi.com/geocoding/v1/" \
          "batch?key={key}{location_list}".format(key=api, location_list=location_list)
    # print(url)
    request = requests.get(url)
    reply = request.json()

    response_list = list()
    for result in reply['results']:
        loc = re.sub("\D", "", result['providedLocation']['location'])
        for location in result['locations']:
            # Let's only append valid ZIP Code lookups
            if location['adminArea3'] != "":
                response_list.append({'location': loc,
                                      'latlng': location['latLng']})

    return response_list


def get_lat_lon_zip(zipcode):
    """
    Returns a dictionary with latitude and longitude of Zipcode, LIMIT 100 ZIP codes!
    :param zipcode: zip code
    :return: dict response {'location:zip, latlng: {lat:lat, lng:lng}}
    """
    api = Api().key
    url = ('http://www.mapquestapi.com/geocoding/v1/'
           'address?key={key}&location={location},US').format(key=api, location=zipcode)
    request = requests.get(url)
    reply = request.json()

    response_dict = dict()
    response_dict['latlng'] = reply['results'][0]['locations'][0]['latLng']
    response_dict['location'] = re.sub("\D", "", reply['results'][0]['providedLocation']['location'])

    return reply['results'][0]['locations'][0]['latLng']


def get_map_with_locations(save_map_name, location_list):
    """
    Use API to save a map from a list of lat/lng list
    :param save_map_name: file name as '[name].jpg'
    :param location_list: list of dictionary pairs {'latlng': {'lat': '', 'lng': ''}}
    :return: saved file in script path file name as save_map_name
    """
    api = Api().key
    loc_list = list()

    for n, loc in enumerate(location_list, 1):
        # print(n, loc['latlng'])
        loc_list.append("{0},{1}|marker-{2}".format(loc['latlng']['lat'],
                                                    loc['latlng']['lng'],
                                                    n))
    loc_list = "||".join(loc_list)
    url = ('https://www.mapquestapi.com/staticmap/v5/'
           'map?key={key}&locations={locations}&size=800,500@2x&format=jpg').format(key=api, locations=loc_list)

    http = urllib3.PoolManager()

    with http.request('GET', url, preload_content=False) as r, open(save_map_name, 'wb') as out_file:
        shutil.copyfileobj(r, out_file)


def main():
    # get_lat_lon_zip(50312)

    locations = [{'location': '50111', 'latlng': {'lat': 41.683934, 'lng': -93.789256}},
                 {'location': '50312', 'latlng': {'lat': 41.585489, 'lng': -93.674747}}]

    get_map_with_locations('test.jpg', locations)


if __name__ == '__main__':
    main()
