from flask import Flask, request, jsonify, send_from_directory
from pytube import YouTube
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    key = request.args.get('key')

    if key != "SHOHAGVAII":
        return jsonify({"error": "Invalid API key!"}), 403

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
        unique_filename = f"{uuid.uuid4()}.mp4"
        save_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
        stream.download(output_path=DOWNLOAD_FOLDER, filename=unique_filename)

        return jsonify({
            "file_url": f"/file/{unique_filename}",
            "filename": stream.default_filename,
            "message": "Download started"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/file/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
