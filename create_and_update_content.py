import os
from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image, ImageDraw, ImageFont
import pathlib
cwd = pathlib.Path(__file__).parent.resolve()

print(cwd)

JPG = os.path.join(cwd, "thumbnail.jpg")
JPGFINAL = os.path.join(cwd, "thumbnail_final.jpg")
SECRET_JSON = os.path.join(cwd, "client_secret.json")
FONT = os.path.join(cwd, "OpenSans-Bold.ttf")
VIDEO_ID = "USQIWIvR4aA"

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def get_authenticated_service():
    try:
        credentials = Credentials.from_authorized_user_file(SECRET_JSON)
    except ValueError as e:
        flow = InstalledAppFlow.from_client_secrets_file(
            SECRET_JSON, scopes=scopes
        )
        credentials = flow.run_console()
        with open(SECRET_JSON, "w") as file:
            file.write(credentials.to_json())
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def get_views(youtube, video_id):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()
    all_video_stats = []

    for video in response["items"]:
        video_stats = dict(
            views=video["statistics"].get("viewCount"),
            likes=video["statistics"].get("likeCount"),
        )
        all_video_stats.append(video_stats)
    single_vid = all_video_stats[0]
    views = single_vid.get("views")
    likes = single_vid.get("likes")
    return views, likes


def draw(input_image_path, output_path, text1, views, likes):
    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)
    font1 = ImageFont.truetype(FONT, size=110)
    font2 = ImageFont.truetype(FONT, size=120)
    draw.text((50, 310), f"Stand {text1} Uhr:", font=font1)
    draw.text((50, 455), f"ERST {views} views und {likes} Likes?", font=font2)
    image.save(output_path)


def update_description(youtube, title, description, video_id):
    request = youtube.videos().update(
        part="snippet,status",
        body={
            "id": video_id,
            "snippet": {
                "categoryId": 22,
                "defaultLanguage": "de",
                "description": description,
                "title": title,
            },
        },
    )
    request.execute()


def update_thumbnail(youtube, file, video_id):
    request = youtube.thumbnails().set(
        videoId=video_id, media_body=MediaFileUpload(file)
    )
    request.execute()


youtube = get_authenticated_service()
views, likes = get_views(youtube=youtube, video_id=VIDEO_ID)
now = datetime.now()
date_time = f'{now.strftime("%m/%d/%Y, %H:%M")} Uhr'
title = f"WAS? Nur {views} Aufrufe und {likes} Likes am {date_time}?! Da geht noch was!"
description = f"""
Diese Nachricht ist VON PYTHON AUTOMATISCH generiert. Das Video hat am {date_time} {views} Views erreicht. 
Da geht noch ein wenig mehr :-)

Bitte liken, teilen und kommentieren ;-)
"""
draw(JPG, JPGFINAL, text1=date_time, views=views, likes=likes)
update_description(
    youtube=youtube, title=title, description=description, video_id=VIDEO_ID
)
update_thumbnail(youtube=youtube, file=JPGFINAL, video_id=VIDEO_ID)
