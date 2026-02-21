from googleapiclient.discovery import build
import os

class YouTubeService:
    def __init__(self, api_key):
        self.api_key = api_key
        if api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
        else:
            self.youtube = None

    def search_videos(self, query, max_results=5):
        if not self.youtube:
            return "YouTube API key not configured."
        
        try:
            request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                title = item['snippet']['title']
                video_id = item['id']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append(f"- **{title}**\n  [Watch on YouTube]({video_url})")
            
            if not videos:
                return "No videos found for that search."
                
            return "\n\n".join(videos)
            
        except Exception as e:
            error_str = str(e)
            if "referer" in error_str.lower() or "blocked" in error_str.lower():
                return "⚠️ **YouTube API Restriction Error**: Your API key has 'Website Restrictions' enabled in Google Cloud Console. \n\n**To fix this:**\n1. Go to [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials).\n2. Edit your YouTube API Key.\n3. Under 'Application restrictions', set it to **'None'** for local testing.\n4. Save and try again."
            return f"Error searching YouTube: {error_str}"

    def get_trending_videos(self, region_code='US', max_results=5):
        if not self.youtube:
            return "YouTube API key not configured."
            
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                title = item['snippet']['title']
                video_id = item['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append(f"- **{title}**\n  [Watch on YouTube]({video_url})")
                
            return "\n\n".join(videos)
        except Exception as e:
            error_str = str(e)
            if "referer" in error_str.lower() or "blocked" in error_str.lower():
                return "⚠️ **YouTube API Restriction Error**: Your API Key is restricted. Please go to your Google Cloud Console and set 'Application restrictions' to **'None'** for testing."
            return f"Error getting trending videos: {error_str}"
