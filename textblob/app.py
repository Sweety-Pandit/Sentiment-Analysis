import streamlit as st  # Streamlit library for creating the web app
from googleapiclient.discovery import build  # To interact with YouTube API
from langdetect import detect  # Language detection library
import textblob  # Library for sentiment analysis
import re  # Regular expression library for pattern matching

api_key = 'Your_API_Key'  # API key for accessing YouTube Data API

def analyze_sentiment(comments):
    # Function to analyze the sentiment of a list of comments
    sentiments = []  # List to store sentiment polarity values
    for comment in comments:
        analysis = textblob.TextBlob(comment)  # Create a TextBlob object for each comment
        sentiments.append(analysis.sentiment.polarity)  # Append the sentiment polarity of the comment
    return sentiments  # Return the list of sentiment polarity values

def extract_youtube_video_comments(video_id):
    # Function to extract comments from a YouTube video using its video ID
    youtube = build('youtube', 'v3', developerKey=api_key)  # Build the YouTube API client

    video_response = youtube.commentThreads().list(
        part='snippet,replies',  # Fetch comment snippets and replies
        videoId=video_id  # Specify the video ID
    ).execute()  # Execute the API request

    comments = []  # List to store the extracted comments
    while len(comments) <= 100:  # Limit the number of comments to 100
        for item in video_response['items']:  # Iterate through the items in the response
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']  # Extract the comment text
            try:
                if detect(comment) == 'en':  # Check if the comment is in English
                    comments.append(comment)  # Add the comment to the list
            except:
                pass  # Ignore comments that cannot be processed

        # Handle pagination if more comments are available
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',  # Fetch comment snippets and replies
                videoId=video_id,  # Specify the video ID
                pageToken=video_response['nextPageToken']  # Use the next page token
            ).execute()  # Execute the API request for the next page
        else:
            break  # Exit the loop if no more pages are available

    return comments  # Return the list of extracted comments

def analyze_yt_comments(video_id):
    # Function to analyze the sentiment of comments for a given YouTube video
    comments = extract_youtube_video_comments(video_id)  # Extract comments from the video

    sentiment = analyze_sentiment(comments)  # Analyze the sentiment of the comments
    print("Sentiment Analysis of the video comments:")
    avg_sentiment = sum(sentiment) / len(sentiment)  # Calculate the average sentiment polarity

    # Display overall review based on average sentiment
    if avg_sentiment > 0:
        st.success("Overall Review: Positive")
    elif avg_sentiment == 0:
        st.success("Overall Review: Neutral")
    else:
        st.success("Overall Review: Negative")

def extract_video_id(youtube_link):
    # Function to extract the video ID from a YouTube URL
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'  # Regex to match YouTube video ID
    match = re.search(pattern, youtube_link)  # Search for the pattern in the provided link
    if match:
        return match.group(1)  # Return the matched video ID
    else:
        return None  # Return None if no match is found

def is_valid_youtube_link(link):
    # Function to validate a YouTube link
    return bool(re.search(r'[a-zA-Z]', link)) and extract_video_id(link) is not None  # Check if the link contains letters and a valid video ID

st.title("Analyzing Sentiments in Students Reviews of Online Courses")  # Title of the Streamlit app
url = st.text_input("Enter YouTube course video URL")  # Input field for the YouTube video URL
b = st.button("Analyze Sentiment")  # Button to trigger sentiment analysis

if "select" not in st.session_state:
    st.session_state["select"] = False  # Initialize session state for "select"

if not st.session_state["select"]:  # Check if "select" is False
    if b:  # If the button is clicked
        if is_valid_youtube_link(url):  # Validate the YouTube link
            id = extract_video_id(url)  # Extract the video ID
            analyze_yt_comments(id)  # Analyze the sentiments of the video's comments
        else:
            st.error("Invalid URL, Please enter a valid video URL (must contain letters and be a valid YouTube link)")  # Display error message for invalid URL
else:
    st.error("Invalid URL, Please enter a valid video URL")  # Display error message if "select" is True
