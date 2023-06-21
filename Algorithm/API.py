#!/usr/bin/env python3

import requests

class API:
    headers = {
        'Accept': 'application/json'
    }

    def request(link, params):
        return requests.get(link, headers=API.headers, params=params).json()
