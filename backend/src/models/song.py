class Song:
    def __init__(self, spotify_object):
        self.title = spotify_object['name']
        self.artists = spotify_object['artists']
        self.album = spotify_object['album']['name']
        self.album_cover = spotify_object['album']['images'][0]['url']
        self.duration = spotify_object['duration_ms']
