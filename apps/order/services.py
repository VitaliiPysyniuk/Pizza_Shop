import requests
import os


class GeocodingAPI:
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    geocoding_api_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    @staticmethod
    def validate_addresses(address):
        params = {
            'address': address,
            'language': 'uk',
            'key': GeocodingAPI.api_key
        }

        response = requests.get(url=GeocodingAPI.geocoding_api_url, params=params).json()
        result = response['results'][0]

        if 'partial_match' in result.keys() and result['types'][0] != 'street_address':
            raise ValueError('Given delivery address is not valid.')
