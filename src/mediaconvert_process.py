# Import necessary modules
import json
import boto3
import requests
import datetime
from pytube import YouTube
import os
from config import (
    API_URL,             # The endpoint URL for fetching sports highlights
    RAPIDAPI_HOST,       # The host for the RapidAPI service
    RAPIDAPI_KEY,        # The API key for authenticating with RapidAPI
    DATE,                # The date for which to fetch highlights
    LEAGUE_NAME,         # The name of the soccer league (e.g., Major League Soccer)
    LIMIT,               # The maximum number of highlights to fetch
    S3_BUCKET_NAME,      # The name of the S3 bucket where data will be stored
    AWS_REGION,          # The AWS region where the S3 bucket is located
    MEDIACONVERT_ENDPOINT,  # The MediaConvert endpoint URL
    MEDIACONVERT_ROLE_ARN,  # The ARN of the IAM role for MediaConvert
)

# Patch pytube to fix 403 errors
def patch_pytube():
    import pytube
    pytube.__version__ = "15.0.0"  # Fake version to bypass YouTube's checks
    pytube.request.default_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

patch_pytube()

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
            print(f"Bucket {S3_BUCKET_NAME} exists.")
        except Exception:
            print(f"Bucket {S3_BUCKET_NAME} does not exist. Creating...")
            if AWS_REGION == "us-east-1":
                s3.create_bucket(Bucket=S3_BUCKET_NAME)
            else:
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
        stream.download(output_path=output_path, filename='first_video.mp4')
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

def create_mediaconvert_job(input_file):
    try:
        mediaconvert = boto3.client('mediaconvert', endpoint_url=MEDIACONVERT_ENDPOINT)
        job_settings = {
            "OutputGroups": [
                {
                    "Name": "File Group",
                    "Outputs": [
                        {
                            "ContainerSettings": {"Container": "MP4", "Mp4Settings": {}},
                            "VideoDescription": {
                                "CodecSettings": {
                                    "Codec": "H_264",
                                    "H264Settings": {
                                        "RateControlMode": "QVBR",
                                        "MaxBitrate": 5000000,
                                        "QualityTuningLevel": "SINGLE_PASS",
                                        "SceneChangeDetect": "TRANSITION_DETECTION"
                                    }
                                }
                            }
                        }
                    ],
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": f"s3://{S3_BUCKET_NAME}/output-folder/"
                        }
                    }
                }
            ],
            "Inputs": [
                {"FileInput": input_file, "TimecodeSource": "ZEROBASED"}
            ]
        }

        # Serialize datetime fields if any exist
        def serialize_datetime(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        response = mediaconvert.create_job(
            Role=MEDIACONVERT_ROLE_ARN,
            Settings=json.loads(json.dumps(job_settings, default=serialize_datetime))
        )
        print("Job created successfully:", response['Job']['Id'])
    except Exception as e:
        print("Error creating MediaConvert job:", str(e))

def process_highlights():
    print("Fetching highlights...")
    highlights = fetch_highlights()
    if highlights:
        print("Saving highlights to S3...")
        save_to_s3(highlights, "mls_highlights")

        youtube_url = highlights["data"][0]["url"]
        download_path = "s3://mlshighlightsnilsojc123/highlights/mls_highlights.json"
        print("Downloading video from YouTube...")
        video_path = download_youtube_video(youtube_url, download_path)

        if video_path:
            s3_video_key = "highlights/first_video.mp4"
            print("Uploading video to S3...")
            upload_to_s3(video_path, s3_video_key)

            input_file = f"s3://{S3_BUCKET_NAME}/{s3_video_key}"
            print("Creating MediaConvert job...")
            create_mediaconvert_job(input_file)

if __name__ == "__main__":
    process_highlights()

