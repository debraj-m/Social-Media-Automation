import os
import requests
import json
from typing import Optional

class DevtoAuthClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self):
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
