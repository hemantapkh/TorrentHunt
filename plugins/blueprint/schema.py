from .struct import content_struct, search_struct


class Schema:
    def __init__(self, Client):
        self.Client = Client

    def search_message(self, response, language):
        message = ''
        for count, item in enumerate(response.get('items', {})):
            if count >= 20:
                break

            message = search_struct.format(
                count=count+1,
                title=item.get('name')[:100],
                size=item.get('size'),
                seeders=item.get('seeders'),
                leechers=item.get('leechers'),
                torrent_id=item.get('torrentId'),
                link_str=self.Client.LG.STR('size', language),
            ) + message

        return message or self.Client.LG.STR('noResults', language)

    def content_message(self, data, language):
        if not data.get('name'):
            return self.Client.LG.STR('errorFetchingLink', language), False

        message = content_struct.format(
            title=data.get('name'),
            size=data.get('size'),
            seeders=data.get('seeders'),
            leechers=data.get('leechers'),
            uploaded_on=data.get('uploadDate'),
            magnet=data.get('magnetLink'),
            size_str=self.Client.LG.STR('size', language),
            seeders_str=self.Client.LG.STR('seeders', language),
            leechers_str=self.Client.LG.STR('leechers', language),
            uploaded_on_str=self.Client.LG.STR('uploadedOn', language),
        )

        return message, True
