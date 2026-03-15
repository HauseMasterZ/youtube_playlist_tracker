import datetime
import os
from typing import ItemsView
from googleapiclient.discovery import build

youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
playlist_id     = "PLK5tc6FSo174pECpHWftUYDcw5KFk4HLs"
# channel_id      = "your_channel_id"

youtube = build('youtube', 'v3', developerKey=youtube_api_key)

#------------------------------------------------------------------------#
# pl_request = youtube.playlists().list(
#     part= 'contentDetails, snippet',
#     channelId = channel_id,
#     maxResults= 10
#         )

# pl_response = pl_request.execute()

# for item in pl_response['items']:
#     print(item)

#     print( item['snippet']['title'] )
#------------------------------------------------------------------------#
current_time     = datetime.datetime.now()
video_ID_list    = [ ]
video_title_list = [ ]   #List that holds all the titles of the videos of a playlist
nextPageToken    = None

while True:           #Loop through multiple pages of 50-values

    pl_request = youtube.playlistItems().list(
            part       ='contentDetails',
            playlistId = playlist_id,
            maxResults = 50,
            pageToken  = nextPageToken
        )

    pl_response = pl_request.execute()

    vid_ids = [ ]      #Save Video IDs from that page into a list

    for item in pl_response['items']:
        vid_ids.append ( item["contentDetails"]["videoId"] )
        video_ID_list.append ( item["contentDetails"]["videoId"] )

    # print(','.join(vid_ids))   #separate all values in a list with commas
    #------------------------------------------------------------------------#
    vid_request = youtube.videos().list(
            part       = "contentDetails, snippet",
            id         = ','.join(vid_ids),
            maxResults = 50
        )

    vid_response = vid_request.execute()

    for item in vid_response['items']:
        # print(item['snippet']['title'])
        video_title_list.append(item['snippet']['title'])

    nextPageToken = pl_response.get("nextPageToken")
    if not nextPageToken:
        break
#---------------------------------------------------------------------------#
yt_video_dict_list = {str(videoId):str(video_tittle) for videoId,video_tittle in zip(video_ID_list,video_title_list) }
#---------------------------------------------------------------------------#
# ```Test if files exist. If not create them.```

if os.path.isfile('Video_Titles.txt'):
    print ("Video_Titles.txt file exists.")
else:
    print ("Video_Titles.txt file does not exist!...creating the file")
    with open('Video_Titles.txt', 'w') as f:
        pass

if os.path.isfile('Video_Playlist_Data.p'):
    print ("Video_Playlist_Data.p file exists.")
else:
    print ("Video_Playlist_Data.p file does not exist!...creating the file")
    with open('Video_Playlist_Data.p', 'w') as f:
        pass

if os.path.isfile('Video_Titles_Added.txt'):
    print ("Video_Titles_Added.txt file exists.")
else:
    print ("Video_Titles_Added file does not exist!...creating the file")
    with open('Video_Titles_Added.txt', 'w') as f:
        pass

if os.path.isfile('Video_Titles_Removed.txt'):
    print ("Video_Titles_Removed.txt file exists.")
else:
    print ("Video_Titles_Removed.txt file does not exist!...creating the file")
    with open('Video_Titles_Removed.txt', 'w') as f:
        pass
#---------------------------------------------------------------------------#

with open('Video_Playlist_Data.p', 'rb') as file:
    try:
        saved_video_dict_list = pickle.load(file)
    except:
        saved_video_dict_list = {}                 

songs_ids_added   = [ song_id for song_id in yt_video_dict_list    if song_id not in saved_video_dict_list ]
songs_ids_removed = [ song_id for song_id in saved_video_dict_list if song_id not in yt_video_dict_list    ]
songs_added       = [ yt_video_dict_list.get   (song, "Error") for song in songs_ids_added ]
songs_removed     = [ saved_video_dict_list.get(song, "Error") for song in songs_ids_removed ]

if songs_added:
    with open("Video_Titles_Added.txt", "a+", encoding="utf-8") as text_file:
        text_file.write( f"Songs Added on: {current_time} " + "\n\n")
        for index, song in enumerate(songs_added, 1):
            text_file.write(str(index) + ": " + str(song) + "\n")
        text_file.write( "#-----------------------------------------------#\n\n")

if songs_removed:
    with open("Video_Titles_Removed.txt", "a+", encoding="utf-8") as text_file:
        text_file.write( f"Songs Removed on: {current_time} " + "\n\n")
        for index, song in enumerate(songs_removed, 1):
            text_file.write(str(index) + ": " + str(song) + "\n")
        text_file.write( "#-----------------------------------------------#\n\n")

#---------------------------------------------------------------------------#

with open('Video_Playlist_Data.p', 'wb') as file:
    pickle.dump(yt_video_dict_list, file, protocol=pickle.HIGHEST_PROTOCOL)

with open("Video_Titles.txt", "w", encoding="utf-8") as text_file:
    text_file.write( f"Playlist last checked on: {current_time} " + "\n\n")
    for index, song in enumerate(list(yt_video_dict_list.values()), 1):
         text_file.write(str(index) + ": " + str(song) + "\n")   

# if __name__ == "__main__":
#     read_files()
#     get_youtube_data()
#     update_files()
#     print("Done")
