"Get translation of string"

import json


class Lang:
    def __init__(self, json_file, config):
        with open(json_file) as f:
            self.data = json.load(f)

        with open(config) as f:
            self.config = json.load(f)

    def __getattr__(self, name):
        def get_value(key, code="english"):
            return (
                self.data.get(name, {}).get(key, {}).get(code)
                or
                # If translation not available, return english
                self.data.get(name, {}).get(key, {}).get("english")
            )

        return get_value

    def config(self):
        self.config
