from django.shortcuts import render
from django.conf import settings
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from openai import OpenAI
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path

client = OpenAI()

# Function to fetch content from a URL
def fetch_content_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text

# Function to read from file
def read_from_file(path):
    file1 = open(Path.cwd().joinpath(path).resolve(), 'r')
    result = file1.read()
    file1.close()
    return result

@csrf_exempt
# @require_http_methods(["POST"])
def extract_bets(request, video_id):
    # api_key = settings.YOUTUBE_API_KEY
    # youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        # response = youtube.videos().list(
        #     part="contentDetails,snippet",
        #     id=video_id
        # ).execute()

        # items = response.get("items", [])
        # if not items:
        #     return JsonResponse({"error": "No captions found for this video."}, status=404)

        # caption_id = items[0]['id']
        # caption_response = youtube.captions().download(id=caption_id).execute()
        # transcript = caption_response.decode('utf-8')
        # print(transcript)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_list])
        transcript = transcript.replace("\n", " ")


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    # try:
    #     data = json.loads(request.body)
    # except ValueError:
    #     return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Warn if there's no input
    # if "input" not in data:
    #     return JsonResponse({"error": "Missing input parameter"}, status=400)

    # Get data from client
    # input_data = data["input"]

    # Set the system and user URLs
    # system_url = "https://raw.githubusercontent.com/danielmiessler/fabric/main/patterns/extract_wisdom/system.md"
    # user_url = "https://github.com/danielmiessler/fabric/blob/main/patterns/extract_wisdom/dmiessler/extract_wisdom-1.0.0/user.md"

    try:
        # Fetch the prompt content
        system_content = read_from_file('fabrichof/patterns/extract_bets/system.md')
        user_file_content = read_from_file('fabrichof/patterns/extract_bets/user.md')
    except requests.RequestException as e:
        return JsonResponse({"error": f"Error fetching content: {str(e)}"}, status=500)

    # Build the API call
    system_message = {"role": "system", "content": system_content}
    user_message = {"role": "user", "content": user_file_content + "\n" + transcript}
    messages = [system_message, user_message]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.1,
        )
        
        assistant_message = response.choices[0].message.content
        
        return JsonResponse({"response": assistant_message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

