from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
import os
import random

# Initialize Flask app
app = Flask(__name__)

# ✅ Enable CORS globally
CORS(app)

# Initialize YTMusic API
ytmusic = YTMusic()

# 🔍 Search route
@app.route("/search")
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    search_results = ytmusic.search(query)
    songs = []

    for item in search_results:
        if item["resultType"] != "song":
            continue

        song = {
            "title": item["title"],
            "artist": ", ".join([a["name"] for a in item["artists"]]),
            "thumbnail": item["thumbnails"][-1]["url"],
            "videoId": item["videoId"],
            "url": f"https://www.youtube.com/watch?v={item['videoId']}",
        }
        songs.append(song)

    return jsonify(songs)

# 🎵 Get audio stream
@app.route("/getAudio")
def get_audio():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "forceurl": True,
        "noplaylist": True,
        "extract_flat": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            return jsonify({"audioUrl": info_dict["url"]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# 🎧 Get similar songs
@app.route("/getSimilarSongs")
def get_similar_songs():
    song_id = request.args.get("songId")
    if not song_id:
        return jsonify({"error": "Missing 'songId' parameter"}), 400

    try:
        song = ytmusic.get_song(song_id)
        title = song["videoDetails"]["title"]
        artist = song["videoDetails"]["author"]
        query = f"{title} {artist}"

        results = ytmusic.search(query, filter="songs")
        formatted = []

        for item in results:
            if item.get("videoId") == song_id:
                continue

            formatted.append({
                "title": item["title"],
                "artist": ", ".join([a["name"] for a in item["artists"]]),
                "thumbnail": item["thumbnails"][-1]["url"],
                "videoId": item["videoId"],
                "url": f"https://www.youtube.com/watch?v={item['videoId']}",
            })

        return jsonify(formatted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🆕 New releases (mock example)
@app.route("/newReleases")
def new_releases():
    search_results = ytmusic.get_charts("IN")["new_releases"]
    songs = []

    for item in search_results:
        songs.append({
            "title": item["title"],
            "artist": ", ".join([a["name"] for a in item["artists"]]),
            "thumbnail": item["thumbnails"][-1]["url"],
            "videoId": item.get("videoId", ""),
            "url": f"https://www.youtube.com/watch?v={item['videoId']}" if item.get("videoId") else "",
        })

    return jsonify(songs)

# 🔀 Random songs
@app.route("/randomSongs")
def random_songs():
    query = random.choice(["pop", "rock", "chill", "romantic", "lofi"])
    results = ytmusic.search(query, filter="songs")
    songs = []

    for item in results[:15]:
        songs.append({
            "title": item["title"],
            "artist": ", ".join([a["name"] for a in item["artists"]]),
            "thumbnail": item["thumbnails"][-1]["url"],
            "videoId": item["videoId"],
            "url": f"https://www.youtube.com/watch?v={item['videoId']}",
        })

    return jsonify(songs)

# 🌎 Trending (India)
@app.route("/trending")
def trending():
    charts = ytmusic.get_charts("IN")
    trending_songs = charts["songs"]
    songs = []

    for item in trending_songs:
        songs.append({
            "title": item["title"],
            "artist": ", ".join([a["name"] for a in item["artists"]]),
            "thumbnail": item["thumbnails"][-1]["url"],
            "videoId": item.get("videoId", ""),
            "url": f"https://www.youtube.com/watch?v={item['videoId']}" if item.get("videoId") else "",
        })

    return jsonify(songs)

# 🔚 Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # for Render
    app.run(debug=True, host="0.0.0.0", port=port)
