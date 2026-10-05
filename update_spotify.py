#!/usr/bin/env python3
import base64
import json
import os
import re
import urllib.parse
import urllib.request

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]
README_PATH = "README.md"

def get_access_token():
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]

def fetch_top(item_type, token):
    url = f"https://api.spotify.com/v1/me/top/{item_type}?time_range=short_term&limit=5"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8")).get("items", [])

def main():
    token = get_access_token()
    tracks = fetch_top("tracks", token)
    artists = fetch_top("artists", token)

    tracks_lines = [
        f"{i}. [{t['name']}]({t['external_urls']['spotify']}) - **{', '.join([a['name'] for a in t['artists']])}**"
        for i, t in enumerate(tracks, 1)
    ]
    artists_lines = [
        f"{i}. [{a['name']}]({a['external_urls']['spotify']})" + (f" *({', '.join(a['genres'][:2])})*" if a.get('genres') else "")
        for i, a in enumerate(artists, 1)
    ]

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(
        r"<!-- SPOTIFY_TOP_TRACKS:START -->.*?<!-- SPOTIFY_TOP_TRACKS:END -->",
        f"<!-- SPOTIFY_TOP_TRACKS:START -->\n" + "\n".join(tracks_lines) + "\n<!-- SPOTIFY_TOP_TRACKS:END -->",
        content, flags=re.DOTALL
    )
    content = re.sub(
        r"<!-- SPOTIFY_TOP_ARTISTS:START -->.*?<!-- SPOTIFY_TOP_ARTISTS:END -->",
        f"<!-- SPOTIFY_TOP_ARTISTS:START -->\n" + "\n".join(artists_lines) + "\n<!-- SPOTIFY_TOP_ARTISTS:END -->",
        content, flags=re.DOTALL
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
