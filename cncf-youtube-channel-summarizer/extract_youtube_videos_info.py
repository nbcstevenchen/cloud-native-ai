from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import json
from tqdm import tqdm
import os

def get_channel_playlist(youtube, channel_id):
    request = youtube.playlists().list(
        part = "snippet",
        channelId = channel_id,
        maxResults = 50
    )
    response = request.execute()

    playlists = []
    playlists_id = []
    playlists_title = []
    playlists_desc = []
    while request is not None:
        response = request.execute()
        playlists += response["items"]
        request = youtube.playlists().list_next(request, response)


    for items in playlists:
        playlists_id.append(items['id'])
        playlists_title.append(items['snippet']['title'])
        playlists_desc.append(items['snippet']['description'])
    return playlists, playlists_id, playlists_title, playlists_desc

def get_video_id(youtube, playlist_id):
    video_ids = []
    video_titles = []
    video_desc = []
    video_date = []
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50,
                                                         pageToken=next_page_token).execute()
        for item in playlist_response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
            video_titles.append(item['snippet']['title'])
            video_desc.append(item['snippet']['description'])
            video_date.append(item['snippet']['publishedAt'])

       # print(videos)
        next_page_token = playlist_response.get('nextPageToken')
        if next_page_token is None:
            break

    return video_ids, video_titles, video_desc, video_date

def get_video_caption(video_id):
    # List the available captions for the video
    try:
        raw_captions = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        print(f"{video_id} doesn't have a transcript")
        return f"{video_id} doesn't have a transcript"
    captions = ''
    for sentences in raw_captions:
        captions += sentences['text'] + ' '
    return captions

def get_video_info(youtube, CHANNEL_ID):
    play_lists_dict = dict()
    videos_dict = {}
    playlists, playlists_id, playlists_title, playlists_desc = get_channel_playlist(youtube, CHANNEL_ID)
    for i in tqdm(range(0, len(playlists_id))):
        play_lists_dict[playlists_id[i]] = {'title': playlists_title[i], 'description': playlists_desc[i],
                                            'playlists_id': playlists_id[i]}
        video_ids, video_titles, video_desc, video_date = get_video_id(youtube, playlists_id[i])
        for x in range(0, len(video_ids)):
            caption = get_video_caption(video_ids[x])
            videos_dict[video_ids[x]] = {'video_title': video_titles[x], 'video_description': video_desc[x],
                                         'transcript': caption, 'play_list': play_lists_dict[playlists_id[i]], 'published_date': video_date[x]}

    with open("cncf-youtube-channel-summarizer/data/CNCF_video_information_with_date.json", "w") as outfile:
        json.dump(videos_dict, outfile)

if __name__ == "__main__":
    YOUR_API_KEY = os.environ['GOOGLE_API_KEY']  ## GOOGLE_API_KEY for extracting youtube videos.
    CHANNEL_ID = 'UCvqbFHwN-nwalWPjPUKpvTA'   ## This channel id is extracted from  CNCF youtube video url.
    youtube = build('youtube', 'v3', developerKey=YOUR_API_KEY)
    videos_dict = get_video_info(youtube, CHANNEL_ID)