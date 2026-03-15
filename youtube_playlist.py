import datetime
import os
import pickle
from googleapiclient.discovery import build

youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
if not youtube_api_key:
    raise ValueError("YOUTUBE_API_KEY environment variable not set")

playlist_ids = {
    "PLK5tc6FSo174pECpHWftUYDcw5KFk4HLs": "Gym",
    "PLK5tc6FSo175xc8zNBMrUZJIY9Q_K9I4w": "Driving",
    "PLK5tc6FSo177DVG_k_Tx57Ztvh0B-5Drd": "Songs"
}

youtube      = build('youtube', 'v3', developerKey=youtube_api_key)
current_time = datetime.datetime.now()

for playlist_id, playlist_name in playlist_ids.items():
    try:
        folder = playlist_name
        os.makedirs(folder, exist_ok=True)

        data_file    = f"{folder}/Video_Playlist_Data.p"
        titles_file  = f"{folder}/Video_Titles.txt"
        added_file   = f"{folder}/Video_Titles_Added.txt"
        removed_file = f"{folder}/Video_Titles_Removed.txt"

        for file_path in [added_file, removed_file]:
            if not os.path.exists(file_path):
                open(file_path, 'w').close()

        current       = {}
        nextPageToken = None

        while True:
            pl_response = youtube.playlistItems().list(
                part       = 'contentDetails',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken  = nextPageToken
            ).execute()

            vid_ids = [item["contentDetails"]["videoId"] for item in pl_response['items']]

            vid_response = youtube.videos().list(
                part       = "snippet, contentDetails",
                id         = ','.join(vid_ids),
                maxResults = 50
            ).execute()

            for item in vid_response['items']:
                vid_id = item['id']
                current[vid_id] = {
                    "title"     : item['snippet']['title'],
                    "channel"   : item['snippet']['channelTitle'],
                    "published" : item['snippet']['publishedAt'],
                    "duration"  : item['contentDetails']['duration'],
                    "url"       : f"https://www.youtube.com/watch?v={vid_id}"
                }

            nextPageToken = pl_response.get("nextPageToken")
            if not nextPageToken:
                break

        if os.path.exists(data_file):
            with open(data_file, 'rb') as f:
                previous = pickle.load(f)
        else:
            previous = {}

        added   = {sid: current[sid]  for sid in current  if sid not in previous}
        removed = {sid: previous[sid] for sid in previous if sid not in current}

        if added:
            with open(added_file, "a", encoding="utf-8") as f:
                f.write(f"Added on: {current_time}\n\n")
                for i, (vid_id, meta) in enumerate(added.items(), 1):
                    f.write(f"{i}: {meta['title']}\n")
                    f.write(f"   Channel  : {meta['channel']}\n")
                    f.write(f"   Published: {meta['published']}\n")
                    f.write(f"   Duration : {meta['duration']}\n")
                    f.write(f"   URL      : {meta['url']}\n\n")
                f.write("#-----------------------------------------------#\n\n")

        if removed:
            with open(removed_file, "a", encoding="utf-8") as f:
                f.write(f"Removed on: {current_time}\n\n")
                for i, (vid_id, meta) in enumerate(removed.items(), 1):
                    f.write(f"{i}: {meta['title']}\n")
                    f.write(f"   Channel  : {meta['channel']}\n")
                    f.write(f"   Published: {meta['published']}\n")
                    f.write(f"   Duration : {meta['duration']}\n")
                    f.write(f"   URL      : {meta['url']}\n\n")
                f.write("#-----------------------------------------------#\n\n")

        with open(data_file, 'wb') as f:
            pickle.dump(current, f, protocol=pickle.HIGHEST_PROTOCOL)

        with open(titles_file, "w", encoding="utf-8") as f:
            f.write(f"Playlist last checked on: {current_time}\n\n")
            for i, meta in enumerate(current.values(), 1):
                f.write(f"{i}: {meta['title']}\n")

    except Exception as e:
        print(f"Failed to process {playlist_name}: {e}")
        continue
