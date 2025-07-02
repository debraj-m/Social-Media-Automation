import os
import requests
import json
from typing import Optional

class MediumAuthClient:
    # Medium uses integration tokens, not OAuth for most API access
    def __init__(self, integration_token: str):
        self.integration_token = integration_token

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.integration_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
