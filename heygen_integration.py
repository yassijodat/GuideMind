import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HeyGenAPI:
    """HeyGen API integration for GuideMind"""
    
    def __init__(self):
        """Initialize HeyGen API with credentials from .env"""
        self.api_key = os.getenv("HEYGEN_API_KEY")
        self.base_url = "https://api.heygen.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
        
        # Check if API key is available
        if not self.api_key:
            print("Warning: HEYGEN_API_KEY not found in .env file")
    
    def is_authenticated(self):
        """Check if API key is valid"""
        if not self.api_key:
            return False
            
        try:
            # Test the API key with a simple request
            response = requests.get(
                f"{self.base_url}/user_info", 
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def generate_video(self, avatar_id, script, voice_id=None):
        """Generate a video using HeyGen API
        
        Args:
            avatar_id: The ID of the avatar to use
            script: The text content for the avatar to say
            voice_id: Optional voice ID to use (if None, uses avatar's default voice)
            
        Returns:
            The URL of the generated video or None if failed
        """
        if not self.is_authenticated():
            print("Error: Not authenticated with HeyGen API")
            return None
        
        try:
            # Create the video generation payload
            payload = {
                "background": "#ffffff",
                "clips": [
                    {
                        "avatar_id": avatar_id,
                        "avatar_style": "normal",
                        "input_text": script,
                        "voice_id": voice_id,
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity": 0.75
                        }
                    }
                ],
                "ratio": "16:9",
                "test": False,
                "version": "v1"
            }
            
            # Make the API request to generate video
            response = requests.post(
                f"{self.base_url}/video.generate",
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code != 200:
                print(f"Error generating video: {response.text}")
                return None
            
            # Extract video ID from response
            data = response.json()
            video_id = data.get("data", {}).get("video_id")
            
            if not video_id:
                print("Error: No video ID returned")
                return None
            
            # Poll for video status until complete
            return self._wait_for_video(video_id)
            
        except Exception as e:
            print(f"Error generating video: {e}")
            return None
    
    def _wait_for_video(self, video_id, max_attempts=60, delay=5):
        """Wait for video processing to complete
        
        Args:
            video_id: The video ID to check
            max_attempts: Maximum number of status check attempts
            delay: Delay between status checks in seconds
            
        Returns:
            The URL of the completed video or None if failed/timeout
        """
        for attempt in range(max_attempts):
            try:
                # Check video status
                response = requests.get(
                    f"{self.base_url}/video.status",
                    headers=self.headers,
                    params={"video_id": video_id}
                )
                
                if response.status_code != 200:
                    print(f"Error checking video status: {response.text}")
                    return None
                
                data = response.json()
                status = data.get("data", {}).get("status")
                
                if status == "completed":
                    # Video is ready, return the URL
                    return data.get("data", {}).get("video_url")
                elif status == "failed":
                    print("Video generation failed")
                    return None
                
                # Wait before checking again
                print(f"Video processing: {status} ({attempt+1}/{max_attempts})")
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error checking video status: {e}")
                return None
        
        print(f"Timeout waiting for video to complete after {max_attempts} attempts")
        return None
    
    def list_avatars(self):
        """List available avatars
        
        Returns:
            List of available avatars or empty list if failed
        """
        if not self.is_authenticated():
            print("Error: Not authenticated with HeyGen API")
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/avatar.list",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Error listing avatars: {response.text}")
                return []
            
            data = response.json()
            return data.get("data", {}).get("avatars", [])
            
        except Exception as e:
            print(f"Error listing avatars: {e}")
            return []
    
    def list_voices(self):
        """List available voices
        
        Returns:
            List of available voices or empty list if failed
        """
        if not self.is_authenticated():
            print("Error: Not authenticated with HeyGen API")
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/voice.list",
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Error listing voices: {response.text}")
                return []
            
            data = response.json()
            return data.get("data", {}).get("voices", [])
            
        except Exception as e:
            print(f"Error listing voices: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize HeyGen API
    heygen = HeyGenAPI()
    
    # Check authentication
    if heygen.is_authenticated():
        print("Successfully authenticated with HeyGen API")
        
        # List available avatars
        avatars = heygen.list_avatars()
        print(f"Found {len(avatars)} avatars")
        
        # List available voices
        voices = heygen.list_voices()
        print(f"Found {len(voices)} voices")
        
        # Generate a test video if avatars are available
        if avatars:
            avatar_id = avatars[0].get("avatar_id")
            print(f"Generating test video with avatar ID: {avatar_id}")
            
            video_url = heygen.generate_video(
                avatar_id=avatar_id,
                script="Welcome to GuideMind! I'll guide you through the origami instructions step by step."
            )
            
            if video_url:
                print(f"Video generated successfully: {video_url}")
            else:
                print("Failed to generate video")
    else:
        print("Failed to authenticate with HeyGen API")