import spotipy
import json
import config
from datetime import datetime, timedelta

import requests
import json

target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def generate_playlist():
    # Make an HTTP GET request to the specified URL
    url = 'https://api.composer.nprstations.org/v1/widget/5182d007e1c809685c190ee6/playlist?t=1734460933714&prog_id=65b2b8c21359175e321e27ad&limit=50&errorMsg=No+results+found.+Please+modify+your+search+and+try+again.'
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        playlist = [
            {"song": track["trackName"], "artist": track["artistName"]}
            for episode in data.get("playlist", [])
            if episode.get("date") == target_date
            for track in episode.get("playlist", [])
        ]
        return playlist
    else:
        print("Failed to retrieve the playlist")
        return []

# Example usage
playlist = generate_playlist()
print(json.dumps(playlist, indent=4))

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:8080",
        scope="playlist-modify-private"
    )
)
current_user = sp.current_user()
#create an empty list of track ids
track_ids = []

# Search for each song in the playlist and get the track id
for item in playlist:
    artist, song = item["artist"], item["song"]
    query = f"{song} {artist}" 
    search_results = sp.search(q=query, type="track", limit=10)
    track_ids.append(search_results["tracks"]["items"][0]["id"])


# Create a playlist 
created_playlist = sp.user_playlist_create(
    user=current_user["id"],
    name=f"In the Groove {target_date}",
    public=False
)

# Add track ids to the playlist
sp.user_playlist_add_tracks(
    current_user["id"],
    created_playlist["id"],
    track_ids  
)
