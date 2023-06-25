import os
import re
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, jsonify, request

from dotenv import load_dotenv  # type: ignore
import requests
load_dotenv()


app = Flask(__name__)


def get_video_id(url):
    """
     Extract and return the video id from a video url. This is used with the youtube_transcript_api library to get the transcript of the youtube video

     @param url - The url of the video

     @return The video id or None if not found in the url or the url doesn't contain the video
    """
    match = re.search(r"=(\w+)$", url)
    if match:
        return match.group(1)
    else:
        return None


def get_script(video_id, length, word_length):
    """
     Gets the script and max / min length. This is used to determine how long a script should be in the video

     @param video_id - The YouTube video ID of the transcripts
     @param length - The length of the script to get 1 - 4
     @param word_length - The length of the words in the script

     @return A tuple containing the script the max / min length of the script and the min / max length of
    """
    response = YouTubeTranscriptApi.get_transcript(str(video_id))
    concatenated_text = ''
    # Returns a string representing the response.
    for item in response:
        concatenated_text += item['text'] + ' '
    try:
        word_length = int(word_length)
    except:
        pass

    script = concatenated_text.strip()
    # Calculate the minimum and maximum length of the script.
    if length == 1:
        min_length = int(len(script.split()) / 16)
        max_length = min_length + 25
    elif length == 2:
        min_length = int(len(script.split()) / 12)
        max_length = min_length + 50
    elif length == 3:
        min_length = int(len(script.split()) / 8)
        max_length = min_length + 100
    elif length == 4:

        min_length = word_length
        max_length = word_length + 1
    else:
        min_length = 0
        max_length = 0

    return script, max_length, min_length


def get_summary(script, min_length, max_length):
    """
     Get a summary of a script. It is possible to specify min_length and max_length in the parameters

     @param script - The script to run on HuggingFace
     @param min_length - The minimum length of the script to run
     @param max_length - The maximum length of the script to run

     @return The summary of the script as a string or None if the script could not be run on Hugging
    """
    API_KEY = os.getenv("API_KEY")
    AUTH = f"Bearer {API_KEY}"
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": AUTH}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": script,
        "parameters": {
            "min_length": min_length,
            "max_length": max_length
        }
    })

    try:
        return output[0]['summary_text']
    except:
        print(output)
        sys.exit()


def process_video(url: str, option: int, word_length: int, check_grammar_var: bool = True):
    """
     Process a video URL and chosen option. This function is used to process a video URL and the option that is used to determine the video ID

     @param url - URL of the video to process
     @param option - option that is used to determine the video ID
     @param word_length - length of the word that is used to determine the video ID
     @param check_grammar_var - if True the grammar is checked

     @return summarized video ID or None if grammar is not checked for the video ID ( default : True
    """
    # Process the video URL and chosen option
    id = get_video_id(url=url)

    data = get_script(video_id=id, length=option, word_length=word_length)

    summary = get_summary(
        script=data[0], min_length=data[2], max_length=data[1])

    # Check if the grammar variable is present in the script.
    if check_grammar_var == True:
        summary = check_grammar(script=summary)

        return summary
    else:
        return summary


def check_grammar(script):
    """
     Checks the grammar of a script using the HuggingFace API.

     @param script - The script to check.

     @return The output of the API or None if there was an error. It's a dictionary with the following keys : generated_text : The generated
    """
    API_KEY = os.environ.get('API_KEY')
    AUTH = f"Bearer {API_KEY}"
    API_URL = "https://api-inference.huggingface.co/models/pszemraj/flan-t5-large-grammar-synthesis"
    headers = {"Authorization": AUTH}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": script,
    })
    try:
        return output[0]['generated_text']
    except:
        return output


@app.route('/process_video', methods=['POST'])
def process_video_route():
    """
     Process video and return summary. This is a REST endpoint that can be used to check if a video is valid or not.


     @return JSON with summary of video or error if something went wrong ( not found or invalid url ). Example request **. : http Example response **
    """
    data = request.json
    url = data.get('url')
    option = data.get('option')
    word_length = data.get('word_length')
    check_grammar_var = data.get('check_grammar')

    summary = process_video(url, option, word_length, check_grammar_var)

    return jsonify({'summary': summary})


# @app.route('/check_grammar', methods=['POST'])
# def check_grammar_route():
#     data = request.json
#     script = data.get('script')
#     grammar_corrected_text = check_grammar(script)
#     return jsonify({'grammar_corrected_text': grammar_corrected_text})


# Run the Flask application.
if __name__ == '__main__':

    app.run()
