from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

yt = YTMusic()  # or use setup() if using browser cookies


# ---------------- GET AUDIO ROUTE ----------------
@app.route("/getAudio")
def get_audio():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "extract_flat": True,
        "noplaylist": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"audioUrl": info["url"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- SEARCH ROUTE ----------------
@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = yt.search(query, filter="songs")

    songs = []
    for item in results:
        songs.append(
            {
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": ", ".join([a["name"] for a in item.get("artists", [])]),
                "thumbnail": item.get("thumbnails", [{}])[-1].get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
            }
        )

    return jsonify(songs)


# ---------------- MUSIC SECTION ROUTE ----------------
@app.route("/musicSection")
def music_section():
    data = yt.get_mood_playlists()
    playlists = data.get("moods", [])[0].get("playlists", [])

    songs = []
    for playlist in playlists:
        playlist_data = yt.get_playlist(playlist["playlistId"])
        for item in playlist_data.get("tracks", []):
            songs.append(
                {
                    "id": item.get("videoId"),
                    "title": item.get("title"),
                    "artist": ", ".join([a["name"] for a in item.get("artists", [])]),
                    "thumbnail": item.get("thumbnails", [{}])[-1].get("url", ""),
                    "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
                }
            )

    return jsonify(songs[:20])


# ---------------- NEW RELEASED SONGS ----------------
@app.route("/newReleasedSongs")
def new_released():
    albums = yt.get_charts("new_releases", "IN").get("albums", [])
    songs = []

    for album in albums:
        songs.append(
            {
                "id": album.get("browseId"),
                "title": album.get("title"),
                "artist": album.get("artists", [{}])[0].get("name", ""),
                "thumbnail": album.get("thumbnails", [{}])[-1].get("url", ""),
            }
        )

    return jsonify(songs[:20])


# ---------------- TRENDING SONGS ----------------
@app.route("/trendingSongs")
def trending_songs():
    trending = yt.get_charts(country="IN").get("songs", [])
    songs = []

    for item in trending:
        songs.append(
            {
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": ", ".join([a["name"] for a in item.get("artists", [])]),
                "thumbnail": item.get("thumbnails", [{}])[-1].get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
            }
        )

    return jsonify(songs[:20])


# ---------------- RANDOM SONGS (Shuffle-like) ----------------
@app.route("/randomSongs")
def random_songs():
    results = yt.search("bollywood songs", filter="songs")
    import random

    random.shuffle(results)

    songs = []
    for item in results[:20]:
        songs.append(
            {
                "id": item.get("videoId"),
                "title": item.get("title"),
                "artist": ", ".join([a["name"] for a in item.get("artists", [])]),
                "thumbnail": item.get("thumbnails", [{}])[-1].get("url", ""),
                "url": f"https://www.youtube.com/watch?v={item.get('videoId')}",
            }
        )

    return jsonify(songs)


# ---------------- RUN FLASK ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # for Render
    app.run(debug=True, host="0.0.0.0", port=port)
