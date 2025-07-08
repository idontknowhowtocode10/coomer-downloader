from flask import Flask, request, send_file, abort
import io, zipfile, requests
from bs4 import BeautifulSoup
from mangum import Mangum

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://coomer.su/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

@app.route("/", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url", "")
    if "coomer.su" not in url:
        abort(400, "Invalid URL")

    # Use full headers here
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    media = [t.get("src") for t in soup.find_all(("img", "source")) if t.get("src", "").startswith("http")]

    if not media:
        abort(404, "No media found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for i, m in enumerate(media, 1):
            try:
                r = requests.get(m, headers=HEADERS)
                r.raise_for_status()
                ext = m.split(".")[-1].split("?")[0]
                buf_name = f"media_{i}.{ext}"
                z.writestr(buf_name, r.content)
            except Exception as e:
                print(f"Failed to download {m}: {e}")
                continue

    buf.seek(0)
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="media.zip")

handler = Mangum(app)
