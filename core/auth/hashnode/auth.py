import os
import requests
import json
from typing import Optional

class HashnodeAuthClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
