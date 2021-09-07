import requests


class Distance:
    api_key = 'AIzaSyATtXEM2gWMdhxjky2KMF7ebfJ58WmevQE'
    direction_api_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

    @staticmethod
    def get_distance_and_duration_between_addresses(self, start_address, end_address, mode, language):
        params = {
            'origins': start_address,
            'destinations': end_address,
            'mode': mode,
            'language': language,
            'key': Distance.api_key
        }

        response = requests.get(url=Distance.direction_api_url, params=params).json()
        print(response)
