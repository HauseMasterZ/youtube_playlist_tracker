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
    video_ID_list    = []
    video_title_list = []
    nextPageToken    = None

    while True:
        pl_response = youtube.playlistItems().list(
            part       = 'contentDetails',
            playlistId = playlist_id,
            maxResults = 50,
            pageToken  = nextPageToken
        ).execute()

        vid_ids = [item["contentDetails"]["videoId"] for item in pl_response['items']]
        video_ID_list.extend(vid_ids)

        vid_response = youtube.videos().list(
            part       = "snippet",
            id         = ','.join(vid_ids),
            maxResults = 50
        ).execute()

        video_title_list.extend([item['snippet']['title'] for item in vid_response['items']])

        nextPageToken = pl_response.get("nextPageToken")
        if not nextPageToken:
            break

    current = {vid: title for vid, title in zip(video_ID_list, video_title_list)}

    data_file = f"{playlist_name}_Video_Playlist_Data.p"
    if os.path.exists(data_file):
        with open(data_file, 'rb') as f:
            previous = pickle.load(f)
    else:
        previous = {}

    added   = {sid: current[sid]  for sid in current  if sid not in previous}
    removed = {sid: previous[sid] for sid in previous if sid not in current}

    if added:
        with open(f"{playlist_name}_Video_Titles_Added.txt", "a", encoding="utf-8") as f:
            f.write(f"Added on: {current_time}\n\n")
            for i, title in enumerate(added.values(), 1):
                f.write(f"{i}: {title}\n")
            f.write("#-----------------------------------------------#\n\n")

    if removed:
        with open(f"{playlist_name}_Video_Titles_Removed.txt", "a", encoding="utf-8") as f:
            f.write(f"Removed on: {current_time}\n\n")
            for i, title in enumerate(removed.values(), 1):
                f.write(f"{i}: {title}\n")
            f.write("#-----------------------------------------------#\n\n")

    with open(data_file, 'wb') as f:
        pickle.dump(current, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open(f"{playlist_name}_Video_Titles.txt", "w", encoding="utf-8") as f:
        f.write(f"Playlist last checked on: {current_time}\n\n")
        for i, title in enumerate(current.values(), 1):
            f.write(f"{i}: {title}\n")
