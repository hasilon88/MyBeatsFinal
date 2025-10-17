import re
from difflib import SequenceMatcher
from ytmusicapi import YTMusic

def normalize(text: str) -> str:
    """Clean text for fair comparison."""
    text = text.lower()
    text = re.sub(r'[\(\)\[\]\{\}\-–_.,!?:;\'\"/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def title_similarity(a: str, b: str) -> float:
    """Return similarity ratio between two strings."""
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def has_common_artist(spotify_artists, yt_artists) -> bool:
    """Check if any artist names overlap."""
    spotify_names = {normalize(a['name']) for a in spotify_artists}
    yt_names = {normalize(a['name']) for a in yt_artists}
    return not spotify_names.isdisjoint(yt_names)

def keyword_penalty(spotify_title: str, yt_title: str) -> float:
    """Penalize mismatched keywords like 'live', 'remix', etc."""
    keywords = ['live', 'remix', 'cover', 'instrumental', 'acoustic']
    s_title, y_title = normalize(spotify_title), normalize(yt_title)
    penalty = 0
    for kw in keywords:
        if kw in y_title and kw not in s_title:
            penalty -= 0.15
    return penalty

def duration_score(spotify_ms: int, yt_seconds: int) -> float:
    """Score based on how close durations are."""
    if not yt_seconds:
        return 0
    spotify_sec = spotify_ms / 1000
    diff = abs(spotify_sec - yt_seconds)
    if diff > 15:
        return 0
    return max(0, 1 - diff / 15)

def match_spotify_to_youtube(song):
    """Find the best YouTube Music match for a Spotify search result item."""
    yt = YTMusic()

    spotify_title = song.title
    spotify_artists = song.artists
    spotify_duration = song.duration

    # Build query (title + all artists)
    artist_names = ' '.join([a['name'] for a in spotify_artists])
    query = f"{spotify_title} {artist_names}"

    # Search only for songs
    results = yt.search(query, filter="songs")
    if not results:
        return None

    best = None
    best_score = 0

    for yt_item in results:
        yt_title = yt_item.get('title', '')
        yt_artists = yt_item.get('artists', [])
        yt_duration = yt_item.get('duration_seconds', 0)
        yt_video_id = yt_item.get('videoId')

        # Compute weighted total score
        t_score = title_similarity(spotify_title, yt_title)
        a_score = 1.0 if has_common_artist(spotify_artists, yt_artists) else 0
        d_score = duration_score(spotify_duration, yt_duration)
        p_score = keyword_penalty(spotify_title, yt_title)

        total_score = (
            t_score * 0.4 +
            a_score * 0.3 +
            d_score * 0.25 +
            p_score
        )

        if total_score > best_score:
            best_score = total_score
            best = yt_item

    if best:
        video_id = best.get('videoId')
        url = f"https://music.youtube.com/watch?v={video_id}" if video_id else None

        return {
            "url": url,
            "song": best
        }

    return None