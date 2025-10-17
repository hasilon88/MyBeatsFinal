from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
import requests

def download_album_cover(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def modify_metadata(file_path, song):
    if isinstance(song.artists, list):
        artist_names = []
        for artist in song.artists:
            if isinstance(artist, dict) and 'name' in artist:
                artist_names.append(artist['name'])
            elif isinstance(artist, str):
                artist_names.append(artist)
        artist_str = ", ".join(artist_names)
    else:
        artist_str = str(song.artists)

    audio = MP3(file_path, ID3=EasyID3)
    audio['title'] = song.title
    audio['artist'] = artist_str
    audio['album'] = song.album
    audio.save()

    try:
        album_cover_data = download_album_cover(song.album_cover)

        audio = MP3(file_path, ID3=ID3)
        try:
            if audio.tags is None:
                audio.add_tags()
        except ID3NoHeaderError:
            audio.add_tags()

        if 'APIC:' in audio.tags:
            audio.tags.delall('APIC')

        mime_type = 'image/jpeg'
        if song.album_cover.lower().endswith('.png'):
            mime_type = 'image/png'

        audio.tags.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc='Cover',
                data=album_cover_data
            )
        )

        audio.save(v2_version=3)
        print(f"✅ Metadata and album art updated for: {song.title}")

    except Exception as e:
        print(f"⚠️ Failed to add album cover: {e}")
