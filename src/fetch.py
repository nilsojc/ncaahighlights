import json
import boto3
import requests
import datetime
from pytube import YouTube
import os
from config import (
    API_URL,
    RAPIDAPI_HOST,
    RAPIDAPI_KEY,
    DATE,
    LEAGUE_NAME,
    LIMIT,
    S3_BUCKET_NAME,
    AWS_REGION,
    MEDIACONVERT_ENDPOINT,
    MEDIACONVERT_ROLE_ARN,
)


def fetch_highlights():
    try:
        query_params = {
            "date": DATE,
            "leagueName": LEAGUE_NAME,
            "limit": LIMIT
        }
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }
        response = requests.get(API_URL, headers=headers, params=query_params, timeout=120)
        response.raise_for_status()
        highlights = response.json()
        print("Highlights fetched successfully!")
        return highlights
    except requests.exceptions.RequestException as e:
        print(f"Error fetching highlights: {e}")
        return None


def save_to_s3(data, file_name):
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        try:
            s3.head_bucket(Bucket=S3_BUCKET_NAME)
        except Exception:
            print(f"Bucket {S3_BUCKET_NAME} does not exist. Creating...")
            s3.create_bucket(
                Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
            )
            print(f"Bucket {S3_BUCKET_NAME} created successfully.")

        s3_key = f"highlights/{file_name}.json"
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        print(f"Highlights saved to S3: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {e}")


def download_youtube_video(url, output_path):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        video_path = os.path.join(output_path, 'video.mp4')
        if not stream:
            print(f"No suitable stream found for URL: {url}")
            return None
        stream.download(output_path=output_path, filename='video.mp4')
        print(f"Video downloaded successfully: {video_path}")
        return video_path
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None


def upload_to_s3(file_path, s3_key):
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        try:
            s3.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            print(f"File already exists in S3: s3://{S3_BUCKET_NAME}/{s3_key}")
            return
        except Exception:
            print(f"File does not exist in S3. Proceeding with upload...")

        s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        print(f"File uploaded to S3: s3://{S3_BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")


def process_highlights():
    print("Fetching highlights...")
    highlights = fetch_highlights()
    if highlights:
        print("Saving highlights to S3...")
        save_to_s3(highlights, "mls_highlights")

    highlights_from_s3 = fetch_highlights()
    if not highlights_from_s3:
        print("Failed to fetch highlights from S3.")
        return

    youtube_url = highlights_from_s3["data"][0]["url"]
    download_path = "/tmp"
    print("Downloading video from YouTube...")
    video_path = download_youtube_video(youtube_url, download_path)

    if video_path:
        s3_video_key = "highlights/first_video.mp4"
        print("Uploading video to S3...")
        upload_to_s3(video_path, s3_video_key)
    else:
        print("Video download failed; skipping upload.")


if __name__ == "__main__":
    process_highlights()



