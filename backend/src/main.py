from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from src.services.youtube_music import match_spotify_to_youtube
from src.services.youtube_downloader import download_youtube_mp3
from src.services.metadata_modifier import modify_metadata
from src.models.song import Song

app = FastAPI()

@app.post("/api/download")
async def process_spotify_track(track_data: dict):
    try:
        song = Song(track_data)

        youtube_info = match_spotify_to_youtube(song)
        if not youtube_info or "url" not in youtube_info:
            raise HTTPException(status_code=404, detail="No YouTube match found")

        file_path = download_youtube_mp3(youtube_info["url"], title=song.title)

        modify_metadata(file_path, song)

        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=f"{song.title}.mp3"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing song: {e}")
