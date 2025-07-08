from flask import Flask, request, send_file, abort
import io, zipfile, requests
from bs4 import BeautifulSoup
from mangum import Mangum

app = Flask(__name__)
USER_AGENT = "Mozilla/5.0"

@app.route("/", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url", "")
    if "coomer.su" not in url:
        abort(400, "Invalid URL")
    resp = requests.get(url, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    media = [t.get("src") for t in soup.find_all(("img", "source")) if t.get("src","").startswith("http")]
    if not media:
        abort(404, "No media found")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for i, m in enumerate(media, 1):
            r = requests.get(m, headers={"User-Agent": USER_AGENT})
            ext = m.split(".")[-1].split("?")[0]
            buf_name = f"media_{i}.{ext}"
            z.writestr(buf_name, r.content)
    buf.seek(0)
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="media.zip")

handler = Mangum(app)
