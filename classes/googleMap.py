import requests
base = "https://maps.google.com/maps/api/geocode/json?latlng={}&language=ja"


def latlng_to_postal_code(latlng):
    req = requests.get(base.format(latlng)).json()
    place = req["results"][0]["address_components"][5]["long_name"]
    return place


def latlng_to_place_data(latlng):
    req = requests.get(base.format(latlng)).json()
    data = req["results"][0]["formatted_address"]
    return data.replace("Unnamed Road,", "")
