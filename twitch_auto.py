import requests
from clip_pipeline import process_clip

CLIENT_ID = "olc3f1h5gt9uetlgn8dyfhesodaura"
CLIENT_SECRET = "9w267r0rdm58b5167x9yp5u6r8ofz9"
STREAMERS = ["serpent"]

def get_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    resp = requests.post(url, params=params)
    resp.raise_for_status()
    return resp.json()["access_token"]

def get_clips(user_login, first=5):
    token = get_oauth_token()
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    resp_user = requests.get("https://api.twitch.tv/helix/users",
                             headers=headers, params={"login": user_login})
    resp_user.raise_for_status()
    user_id = resp_user.json()["data"][0]["id"]

    resp_clips = requests.get("https://api.twitch.tv/helix/clips",
                             headers=headers,
                             params={"broadcaster_id": user_id, "first": first})
    resp_clips.raise_for_status()
    clips = resp_clips.json()["data"]
    return [clip["url"] for clip in clips]

# Verwerk clips
for streamer in STREAMERS:
    clip_urls = get_clips(streamer, first=3)
    for url in clip_urls:
        try:
            output_file = process_clip(url)
            print(f"✅ Clip verwerkt: {output_file}")
        except Exception as e:
            print(f"❌ Fout bij clip {url}: {e}")