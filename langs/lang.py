'Get translation of string'

import json


class Lang:
    def __init__(self, json_file, client):
        self.client = client
        with open(json_file) as f:
            self.data = json.load(f)

    def __getattr__(self, name):
        async def get_value(key, user=None, code=None):
            if user:
                code = await self.client.DB.query(
                    'fetchval',
                    'SELECT language FROM settings WHERE user_id=$1',
                    user.chat.id,
                ) or 'english'

            return self.data.get(name, {}).get(key, {}).get(code)

        return get_value
