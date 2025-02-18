"""
/jackbox/_http.py

    Copyright (c) 2020 ShineyDev
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
        http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import json
import time

import aiohttp
import requests

_SV_URI = "http://ecast.jackboxgames.com/api/v2/rooms/"
_ID_URI = "https://{0}:38203/socket.io/1?t={1}"


class HTTPClient():
    __slots__ = ("client", "logger", "loop", "session")

    def __init__(self, client):
        self.client = client
        self.logger = client.logger
        self.loop = client.loop
        
        # populated in HTTPClient.connect
        self.session = None

    def clear(self):
        self.session = None

    # connection

    async def close(self):
        await self.session.close()

    async def connect(self, code):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
        self.session = aiohttp.ClientSession(headers=headers)

        # room_data

        sv_uri = _SV_URI+code

        print(sv_uri)
        
        payload = {}

        with requests.request("GET", sv_uri, headers=headers, json = payload) as response:
            text = response.text
            
            print(text)
            print('\n\n')

            try:
                room_data = json.loads(text)
                print(json.loads(text))
            except (json.JSONDecodeError) as e:
                raise Exception("invalid room code")

        if room_data["body"]["full"] == "true":
            raise Exception("room full")

        # ws_id

        id_uri = _ID_URI.format(room_data["body"]["host"], int(time.time() * 1000))
        
        with requests.request("GET", id_uri, headers=headers, json = payload, verify=False) as response:
            text = response.text
            print(text)
            ws_id, *_, type = text.split(":")
            
            if not all([n == "60" for (n) in _]):
                await self.close()
                raise Exception("what do these numbers mean")
            elif "websocket" not in type:
                await self.close()
                raise Exception("somehow not websocket")

        return (room_data, ws_id)
