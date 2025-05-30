from flask import Flask, request, jsonify
from pytube import YouTube
import os
import re

app = Flask(__name__)

def sanitize_filename(filename):
    # Remove invalid characters from filename
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@app.route('/')
def home():
    return "YouTube Video Download API is running!"

@app.route('/video_info', methods=['GET'])
def video_info():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        yt = YouTube(video_url)
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "publish_date": yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else None,
            "thumbnail_url": yt.thumbnail_url,
            "streams": []
        }
        
        # Add available streams info
        for stream in yt.streams.filter(progressive=True):
            video_info["streams"].append({
                "itag": stream.itag,
                "resolution": stream.resolution,
                "fps": stream.fps,
                "type": "video+audio" if stream.includes_audio_track else "video",
                "filesize": stream.filesize_mb if hasattr(stream, 'filesize_mb') else None
            })
        
        # Add audio only streams
        for stream in yt.streams.filter(only_audio=True):
            video_info["streams"].append({
                "itag": stream.itag,
                "abr": stream.abr,
                "type": "audio",
                "filesize": stream.filesize_mb if hasattr(stream, 'filesize_mb') else None
            })
        
        return jsonify(video_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/audio', methods=['GET'])
def download_audio():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').last()
        
        if not audio_stream:
            return jsonify({"error": "No audio stream found"}), 404
        
        filename = sanitize_filename(yt.title) + ".mp3"
        audio_stream.download(filename=filename)
        
        return jsonify({
            "title": yt.title,
            "filename": filename,
            "audio_bitrate": audio_stream.abr,
            "filesize": f"{round(audio_stream.filesize / (1024 * 1024), 2)} MB",
            "download_url": f"/downloads/{filename}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/video', methods=['GET'])
def download_video():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').last()
        
        if not video_stream:
            return jsonify({"error": "No video stream found"}), 404
        
        filename = sanitize_filename(yt.title) + ".mp4"
        video_stream.download(filename=filename)
        
        return jsonify({
            "title": yt.title,
            "filename": filename,
            "resolution": video_stream.resolution,
            "filesize": f"{round(video_stream.filesize / (1024 * 1024), 2)} MB",
            "download_url": f"/downloads/{filename}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/video/<itag>', methods=['GET'])
def download_video_by_itag(itag):
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        yt = YouTube(video_url)
        video_stream = yt.streams.get_by_itag(itag)
        
        if not video_stream:
            return jsonify({"error": "Stream with specified itag not found"}), 404
        
        filename = sanitize_filename(yt.title) + ".mp4"
        video_stream.download(filename=filename)
        
        return jsonify({
            "title": yt.title,
            "filename": filename,
            "resolution": video_stream.resolution if hasattr(video_stream, 'resolution') else None,
            "abr": video_stream.abr if hasattr(video_stream, 'abr') else None,
            "filesize": f"{round(video_stream.filesize / (1024 * 1024), 2)} MB",
            "download_url": f"/downloads/{filename}"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/thumbnail', methods=['GET'])
def download_thumbnail():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    try:
        yt = YouTube(video_url)
        thumbnail_url = yt.thumbnail_url
        filename = sanitize_filename(yt.title) + "_thumbnail.jpg"
        
        # In a real implementation, you would download the thumbnail here
        # For simplicity, we're just returning the URL
        
        return jsonify({
            "title": yt.title,
            "thumbnail_url": thumbnail_url,
            "filename": filename,
            "download_url": thumbnail_url  # Direct URL to thumbnail
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
