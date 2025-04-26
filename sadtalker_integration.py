import os
import sys
import json
import time
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SadTalkerAPI:
    """SadTalker API integration for GuideMind
    
    This class handles the generation of talking face videos using SadTalker.
    It supports both local installation and remote API endpoints.
    """
    
    def __init__(self, use_remote_api: bool = True):
        """Initialize SadTalker API
        
        Args:
            use_remote_api: If True, use remote API endpoint; otherwise use local installation
        """
        self.use_remote_api = use_remote_api
        
        # Remote API configuration
        self.remote_api_url = os.getenv("SADTALKER_API_URL", "").strip()
        self.remote_api_key = os.getenv("SADTALKER_API_KEY", "").strip()
        
        # Local installation configuration
        self.sadtalker_path = os.getenv("SADTALKER_PATH", "").strip()
        self.output_dir = os.path.join(tempfile.gettempdir(), "sadtalker_output")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if SadTalker is available
        
        Returns:
            True if SadTalker is available, False otherwise
        """
        if self.use_remote_api:
            return bool(self.remote_api_url and self.remote_api_key)
        else:
            return bool(self.sadtalker_path and os.path.exists(self.sadtalker_path))
    
    def generate_video(self, 
                       source_image: str, 
                       audio_file: str = None,
                       text: str = None,
                       result_file: str = None) -> Optional[str]:
        """Generate a talking face video
        
        Args:
            source_image: Path to the source image
            audio_file: Path to the audio file (if text is not provided)
            text: Text to be spoken (if audio_file is not provided)
            result_file: Path to save the result video (optional)
            
        Returns:
            Path to the generated video or None if failed
        """
        if not self.is_available():
            print("SadTalker is not available")
            return None
        
        if not os.path.exists(source_image):
            print(f"Source image not found: {source_image}")
            return None
        
        if not audio_file and not text:
            print("Either audio_file or text must be provided")
            return None
        
        # If text is provided but not audio_file, generate audio from text
        if text and not audio_file:
            audio_file = self._generate_audio_from_text(text)
            if not audio_file:
                print("Failed to generate audio from text")
                return None
        
        if not os.path.exists(audio_file):
            print(f"Audio file not found: {audio_file}")
            return None
        
        # Generate result filename if not provided
        if not result_file:
            timestamp = int(time.time())
            result_file = os.path.join(self.output_dir, f"result_{timestamp}.mp4")
        
        # Generate video using remote API or local installation
        if self.use_remote_api:
            return self._generate_video_remote(source_image, audio_file, result_file)
        else:
            return self._generate_video_local(source_image, audio_file, result_file)
    
    def _generate_audio_from_text(self, text: str) -> Optional[str]:
        """Generate audio from text using TTS
        
        Args:
            text: Text to be spoken
            
        Returns:
            Path to the generated audio file or None if failed
        """
        try:
            # Import TTS only when needed to avoid unnecessary dependencies
            from TTS.api import TTS
            
            # Create temporary file for audio
            audio_file = os.path.join(self.output_dir, f"speech_{int(time.time())}.wav")
            
            # Initialize TTS
            tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
            
            # Generate audio
            tts.tts_to_file(text=text, file_path=audio_file)
            
            return audio_file
        except Exception as e:
            print(f"Error generating audio from text: {e}")
            
            # Try alternative method using espeak (Unix systems)
            try:
                audio_file = os.path.join(self.output_dir, f"speech_{int(time.time())}.wav")
                subprocess.run(["espeak", "-w", audio_file, text], check=True)
                return audio_file
            except Exception as e2:
                print(f"Error with alternative TTS method: {e2}")
                return None
    
    def _generate_video_remote(self, source_image: str, audio_file: str, result_file: str) -> Optional[str]:
        """Generate video using remote API
        
        Args:
            source_image: Path to the source image
            audio_file: Path to the audio file
            result_file: Path to save the result video
            
        Returns:
            Path to the generated video or None if failed
        """
        try:
            # Prepare files for upload
            with open(source_image, 'rb') as f:
                source_image_data = base64.b64encode(f.read()).decode('utf-8')
            
            with open(audio_file, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Prepare request data
            data = {
                'source_image': source_image_data,
                'audio_data': audio_data,
                'api_key': self.remote_api_key,
                'enhancer': 'gfpgan',  # Optional face enhancer
                'preprocess': 'full',   # Face detection mode
                'still': False,         # Whether to disable head pose motion
                'pose_style': 0,        # Style of the pose motion transfer
            }
            
            # Send request to remote API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.remote_api_key}'
            }
            
            response = requests.post(
                self.remote_api_url,
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code != 200:
                print(f"Error from remote API: {response.text}")
                return None
            
            # Parse response
            result = response.json()
            
            if 'video_data' not in result:
                print(f"Invalid response from remote API: {result}")
                return None
            
            # Save video data to result file
            video_data = base64.b64decode(result['video_data'])
            with open(result_file, 'wb') as f:
                f.write(video_data)
            
            return result_file
        except Exception as e:
            print(f"Error generating video using remote API: {e}")
            return None
    
    def _generate_video_local(self, source_image: str, audio_file: str, result_file: str) -> Optional[str]:
        """Generate video using local SadTalker installation
        
        Args:
            source_image: Path to the source image
            audio_file: Path to the audio file
            result_file: Path to save the result video
            
        Returns:
            Path to the generated video or None if failed
        """
        try:
            # Save current working directory
            cwd = os.getcwd()
            
            # Change to SadTalker directory
            os.chdir(self.sadtalker_path)
            
            # Prepare command
            cmd = [
                sys.executable, 'inference.py',
                '--source_image', source_image,
                '--driven_audio', audio_file,
                '--result_dir', os.path.dirname(result_file),
                '--result_video', os.path.basename(result_file),
                '--enhancer', 'gfpgan',  # Optional face enhancer
                '--preprocess', 'full',   # Face detection mode
                '--still', 'False',       # Whether to disable head pose motion
                '--pose_style', '0',      # Style of the pose motion transfer
            ]
            
            # Run SadTalker
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Change back to original directory
            os.chdir(cwd)
            
            # Check if result file exists
            if os.path.exists(result_file):
                return result_file
            else:
                print(f"Result file not found: {result_file}")
                print(f"Command output: {process.stdout}")
                print(f"Command error: {process.stderr}")
                return None
        except Exception as e:
            # Make sure to go back to original directory
            try:
                os.chdir(cwd)
            except:
                pass
            
            print(f"Error generating video using local installation: {e}")
            return None

# Simple test function
if __name__ == "__main__":
    # Test SadTalker API
    api = SadTalkerAPI(use_remote_api=True)
    
    if api.is_available():
        print("SadTalker API is available")
        
        # Set up test paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_image = os.path.join(current_dir, "static", "img", "avatar-placeholder.jpg")
        
        # Create test image if it doesn't exist
        if not os.path.exists(test_image):
            os.makedirs(os.path.dirname(test_image), exist_ok=True)
            # Download a sample image
            try:
                response = requests.get("https://thispersondoesnotexist.com/", stream=True)
                if response.status_code == 200:
                    with open(test_image, 'wb') as f:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                    print(f"Created test image: {test_image}")
                else:
                    print(f"Error downloading test image: {response.status_code}")
            except Exception as e:
                print(f"Error creating test image: {e}")
        
        # Test with text
        result = api.generate_video(
            source_image=test_image,
            text="Hello, I'm your origami instructor. Let me guide you through making a paper crane."
        )
        
        if result:
            print(f"Generated video: {result}")
        else:
            print("Failed to generate video")
    else:
        print("SadTalker API is not available")
        
        # Print setup instructions
        if api.use_remote_api:
            print("\nTo use remote API, set the following environment variables:")
            print("SADTALKER_API_URL=<remote_api_url>")
            print("SADTALKER_API_KEY=<remote_api_key>")
        else:
            print("\nTo use local installation, set the following environment variables:")
            print("SADTALKER_PATH=<path_to_sadtalker_directory>")