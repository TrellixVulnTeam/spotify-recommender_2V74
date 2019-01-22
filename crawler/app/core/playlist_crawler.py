import spotipy
import spotipy.util
import json
from core.spotify_track import SpotifyTrack


class PlaylistCrawler(object):

    __sp = None
    __first_page = None
    tracks = None

    def __init__(self, username, playlist_url, audio_path='./audio'):
        if not username:
            raise ValueError('Spotify username not set.')
        if not playlist_url:
            raise ValueError('Spotify playlist URL not set.')
        self.__username = username
        self.__playlist_url = playlist_url
        if audio_path[-1] == '/':
            self.audio_path = audio_path[:-1]
        else:
            self.audio_path = audio_path

    def auth_spotify(self):
        token = spotipy.util.prompt_for_user_token(self.__username)
        if token:
            self.__sp = spotipy.Spotify(auth=token)

    def load_first_page(self):
        ''' Load json of first page of playlist at `__playlist_url`.
        '''
        if not self.__sp:
            self.auth_spotify()
        self.__first_page = self.__sp.user_playlist_tracks(
            'spotify',
            playlist_id=self.__playlist_url)

    def parse_json(self):
        ''' Parse fields for each track in the playlist.

        This method parses the json representation of the playlist and creates
        an array of `SpotifyTrack` objects as an instance variable.

        '''
        def parse_page(page):
            for item in page['items']:
                track = item['track']
                if track['preview_url']:
                    self.tracks.append(SpotifyTrack.from_json(track))

        if not self.tracks:
            self.tracks = []

        if not self.__first_page:
            self.load_first_page()

        parse_page(self.__first_page)
        current_page = self.__first_page
        print(current_page['next'])
        while current_page['next']:
            currrent_page = self.__sp.next(current_page)
            parse_page(current_page)

    def download_previews(self):
        if not self.audio_path:
            raise ValueError('No path to write audio is defined.')
        if not self.tracks:
            self.parse_json()

        for track in self.tracks:
            track.download_preview(self.audio_path)

    def __repr__(self):
        return json.dumps(self.__dict__)

