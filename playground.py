"""Downloads a child's photos and videos from Playground (app.tryplayground.com).

Playground's web app is a thin client over a JSON API, so unlike Procare this needs no
browser: sign in through Firebase Auth, then page through the child's media posts.
"""
import os
import tempfile
from datetime import datetime, timedelta

import requests

# Public web-app configuration, from the JS bundle served by app.tryplayground.com
API_URL = "https://api.tryplayground.com/api"
WEB_APP_URL = "https://app.tryplayground.com"
# The API sits behind Cloudflare, which rejects requests that don't look like the web app's
BROWSER_HEADERS = {
    "Accept": "application/json",
    "Origin": WEB_APP_URL,
    "Referer": f"{WEB_APP_URL}/",
    "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0 Safari/537.36",
}
PAGE_SIZE = 50  # Same page size as the web app's media gallery
# Feed posts that can carry images but aren't photos of the kids; the web gallery hides these too
SKIPPED_POST_TYPES = {"signature", "staffCheckin"}


class PlaygroundClient:
    def __init__(self, email, password):
        self.session = requests.Session()
        self.session.headers.update(BROWSER_HEADERS)

        # Playground's public Firebase web API key: productionConfig.apiKey in the web app's JS bundle
        api_key = os.environ["PLAYGROUND_FIREBASE_API_KEY"]
        response = self.session.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=30,
        )
        if not response.ok:
            raise RuntimeError(f"Playground login failed: {response.text[:200]}")
        auth = response.json()

        mapping = self._request("POST", "/public/account", json={"authId": auth["localId"]})
        self.school_id = mapping["schoolId"]
        self.account_id = mapping["accountId"]
        self.session.headers["Authorization"] = f"Bearer {auth['idToken']}"
        self.session.headers["accountid"] = self.account_id
        print("Logged in to Playground.")

    def _request(self, method, path, params=None, **kwargs):
        response = self.session.request(
            method, f"{API_URL}{path}", params={**(params or {}), "origin": "web"}, timeout=60, **kwargs
        )
        response.raise_for_status()
        return response.json()

    def student_ids(self):
        account = self._request("GET", f"/{self.school_id}/account", params={"accountId": self.account_id})["account"]
        return [s if isinstance(s, str) else s["studentId"] for s in account.get("students", [])]

    def media(self, student_id, start, end):
        """Yields (post timestamp in ms, attachment) for photos and videos posted in [start, end)."""
        start_ms, end_ms = int(start.timestamp() * 1000), int(end.timestamp() * 1000)
        # Posts come newest first; startAfter skips everything posted after the range
        params = {"limit": PAGE_SIZE, "mediaOnly": "true", "studentId": student_id, "startAfter": end_ms}
        while True:
            page = self._request("GET", f"/{self.school_id}/posts", params=params)
            posts = page.get("data") or []
            for post in posts:
                if not start_ms <= post["timestamp"] < end_ms or post.get("type") in SKIPPED_POST_TYPES:
                    continue
                for attachment in post.get("attachments") or []:
                    if attachment.get("type") in ("image", "video"):
                        yield post["timestamp"], attachment
            # Stop once a page reaches back past the start of the range
            if len(posts) < PAGE_SIZE or not page.get("cursor") or min(p["timestamp"] for p in posts) < start_ms:
                return
            params.update(startAfter=page["cursor"], cursorPostId=page["cursorPostId"])


def date_range(mode, target_year, target_month, target_day, tz):
    """Start and end of the day (or, in monthly mode, the month) to download, in local time."""
    year, month = int(target_year), datetime.strptime(target_month, "%b").month
    if mode.lower() == "monthly":
        start = datetime(year, month, 1, tzinfo=tz)
        end = datetime(year + month // 12, month % 12 + 1, 1, tzinfo=tz)
    else:
        start = datetime(year, month, int(target_day), tzinfo=tz)
        end = start + timedelta(days=1)
    return start, end


def download_media(email, password, start, end, tz, webdav_client, remote_folder, dry_run=False):
    """Uploads photos and videos posted in [start, end) that aren't already in remote_folder."""
    client = PlaygroundClient(email, password)

    media = {}
    for student_id in client.student_ids():
        for timestamp, attachment in client.media(student_id, start, end):
            name = attachment.get("fileName") or os.path.basename(attachment["path"])
            # Prefix the posting time so the folder sorts chronologically; the name stays stable
            # across runs, which is what lets us skip files that were already uploaded
            posted = datetime.fromtimestamp(timestamp / 1000, tz)
            media[f"{posted:%Y%m%d-%H%M%S}_{name}"] = attachment["url"]
    print(f"Found {len(media)} photos/videos posted from {start:%Y-%m-%d} to {end:%Y-%m-%d} (exclusive).")

    existing = set(webdav_client.list(remote_folder)) if webdav_client.check(remote_folder) else set()
    to_upload = sorted(name for name in media if name not in existing)
    print(f"{len(media) - len(to_upload)} already in {remote_folder}; {len(to_upload)} to upload.")

    for i, filename in enumerate(to_upload, 1):
        remote_path = f"{remote_folder}/{filename}"
        if dry_run:
            print(f"[dry run] Would upload {remote_path}")
            continue
        print(f"Uploading {i}/{len(to_upload)} to {remote_path}")
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                # Pre-signed storage URL: fetched without the Playground session or its credentials
                with requests.get(media[filename], stream=True, timeout=300) as response:
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=1 << 20):
                        temp_file.write(chunk)
                temp_file.flush()
                webdav_client.upload(remote_path=remote_path, local_path=temp_file.name)
        except Exception as e:
            print(f"Could not upload {filename}: {e}")
