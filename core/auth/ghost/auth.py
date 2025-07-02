import os
import requests
import json
from typing import Optional

class GhostAuthClient:
    def __init__(self, admin_api_key: str, api_url: str):
        self.admin_api_key = admin_api_key
        self.api_url = api_url

    def get_headers(self):
        return {
            "Authorization": f"Ghost {self.admin_api_key}",
            "Content-Type": "application/json"
        }
