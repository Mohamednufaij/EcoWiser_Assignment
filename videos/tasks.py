from celery import shared_task

from .models import Video
import subprocess
import boto3
from django.conf import settings

@shared_task
def process_video(video_id):
    video = Video.objects.get(id=video_id)
    input_file = video.file.path
    output_file = input_file.replace('.mp4', '.srt')

    # Run ccextractor command
    subprocess.run(['ccextractor', input_file, '-o', output_file])

    # Upload video and subtitles to S3
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    s3.upload_file(input_file, settings.AWS_STORAGE_BUCKET_NAME, f'videos/{video.file.name}')
    s3.upload_file(output_file, settings.AWS_STORAGE_BUCKET_NAME, f'subtitles/{video.file.name.replace(".mp4", ".srt")}')

    # Extract subtitles and store in DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_S3_REGION_NAME)
    table = dynamodb.Table('Subtitles')

    with open(output_file, 'r') as f:
        subtitles = f.read()

    table.put_item(
        Item={
            'VideoId': str(video.id),
            'Subtitles': subtitles
        }
    )