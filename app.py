import os
import io
import zipfile
from flask import Flask, request, render_template, send_file, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = os.urandom(24)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    profile_url = request.json.get('url')
    if not profile_url or "coomer.su" not in profile_url:
        return jsonify({"error": "Please enter a valid coomer.su profile URL."}), 400

    try:
        headers = {'User-Agent': USER_AGENT}
        resp = requests.get(profile_url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        media_urls = []
        for img in soup.select('img'):
            src = img.get('src')
            if src and src.startswith('http'):
                media_urls.append(src)

        for vid in soup.select('video source'):
            vsrc = vid.get('src')
            if vsrc and vsrc.startswith('http'):
                media_urls.append(vsrc)

        if not media_urls:
            return jsonify({"error": "No media found on this profile."}), 404

        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, mode='w') as zf:
            for idx, murl in enumerate(media_urls, start=1):
                r = requests.get(murl, headers=headers)
                r.raise_for_status()
                ext = murl.split('.')[-1].split('?')[0]
                fname = f"media_{idx}.{ext}"
                zf.writestr(fname, r.content)

        zip_io.seek(0)
        return send_file(
            zip_io,
            mimetype='application/zip',
            as_attachment=True,
            download_name='coomer_profile_media.zip'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
