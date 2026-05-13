from flask import Flask, render_template, request, send_file, jsonify, Response
import yt_dlp
import os
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url')
    format_type = data.get('format')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Pehle title nikalo
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')

        # Title clean karo
        clean_title = title.replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '-').replace('?', '-').replace('"', '-').replace('<', '-').replace('>', '-').replace('|', '-')
        download_name = f"{clean_title}-aaybee.{format_type}"
        
        # File path fix karo
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{clean_title}-aaybee.{format_type}")

        if format_type == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, f"{clean_title}-aaybee.%(ext)s"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }

        elif format_type == 'mp4':
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, f"{clean_title}-aaybee.%(ext)s"),
                'quiet': True
            }

        else:
            return jsonify({'error': 'Invalid format'}), 400

        # Download karo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 1 second wait karo
        time.sleep(1)

        # File read karo
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # File delete karo
            try:
                os.remove(file_path)
            except:
                pass

            # Response bhejo
            mimetype = 'audio/mpeg' if format_type == 'mp3' else 'video/mp4'
            response = Response(
                file_data,
                mimetype=mimetype,
                headers={
                    'Content-Disposition': f'attachment; filename="{download_name}"',
                    'Content-Length': len(file_data)
                }
            )
            return response

        return jsonify({'error': 'File not found after download'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))