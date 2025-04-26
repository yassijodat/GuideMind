import os
import time
import tempfile
import json
import base64
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from sadtalker_integration import SadTalkerAPI

class SadTalkerController:
    """Controller for managing SadTalker integration with GuideMind"""
    
    def __init__(self):
        """Initialize SadTalker controller"""
        # Use remote API by default (can be configured in .env)
        use_remote_api = os.getenv("SADTALKER_USE_REMOTE", "true").lower() == "true"
        self.sadtalker = SadTalkerAPI(use_remote_api=use_remote_api)
        
        # Check if SadTalker is available
        self.initialized = self.sadtalker.is_available()
        
        # Set up video caching
        self.video_cache = {}
        self.cache_dir = os.path.join(tempfile.gettempdir(), "sadtalker_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Default avatar image
        self.avatar_image = os.getenv("SADTALKER_AVATAR_IMAGE", "")
        
        # Directory for avatar images
        self.avatars_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img", "avatars")
        os.makedirs(self.avatars_dir, exist_ok=True)
        
        # Load available avatars
        self.available_avatars = self._load_available_avatars()
        
        # Set default avatar if not set and avatars are available
        if not self.avatar_image and self.available_avatars:
            self.avatar_image = self.available_avatars[0]["path"]
    
    def is_available(self) -> bool:
        """Check if SadTalker is available
        
        Returns:
            True if SadTalker is available, False otherwise
        """
        return self.initialized
    
    def _load_available_avatars(self) -> List[Dict[str, str]]:
        """Load available avatar images
        
        Returns:
            List of avatar dictionaries with id, name, and path
        """
        avatars = []
        
        try:
            # Check if avatars directory exists
            if not os.path.exists(self.avatars_dir):
                return avatars
            
            # List image files in avatars directory
            for filename in os.listdir(self.avatars_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    avatar_id = os.path.splitext(filename)[0]
                    avatar_path = os.path.join(self.avatars_dir, filename)
                    
                    # Create readable name from filename
                    name = avatar_id.replace('_', ' ').replace('-', ' ').title()
                    
                    avatars.append({
                        "id": avatar_id,
                        "name": name,
                        "path": avatar_path
                    })
            
            # Sort avatars by name
            avatars.sort(key=lambda x: x["name"])
        except Exception as e:
            print(f"Error loading avatars: {e}")
        
        return avatars
    
    def get_avatar_options(self) -> List[Dict[str, str]]:
        """Get available avatar options for UI selection
        
        Returns:
            List of avatar dictionaries with id, name, and thumbnail_url
        """
        # Convert avatar paths to web URLs
        result = []
        for avatar in self.available_avatars:
            # Extract filename from path for URL
            filename = os.path.basename(avatar["path"])
            
            result.append({
                "id": avatar["id"],
                "name": avatar["name"],
                "thumbnail": f"/static/img/avatars/{filename}"
            })
        
        return result
    
    def set_avatar(self, avatar_id: str) -> bool:
        """Set the avatar to use for video generation
        
        Args:
            avatar_id: ID of the avatar to use
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            print("SadTalker is not initialized")
            return False
        
        # Find avatar with matching ID
        for avatar in self.available_avatars:
            if avatar["id"] == avatar_id:
                self.avatar_image = avatar["path"]
                return True
        
        print(f"Avatar not found: {avatar_id}")
        return False
    
    def upload_custom_avatar(self, image_data: bytes, name: str = None) -> Optional[Dict[str, str]]:
        """Upload a custom avatar image
        
        Args:
            image_data: Image data as bytes
            name: Name for the avatar (optional)
            
        Returns:
            Avatar dictionary with id, name, and thumbnail_url if successful, None otherwise
        """
        if not self.initialized:
            print("SadTalker is not initialized")
            return None
        
        try:
            # Generate unique ID for avatar
            avatar_id = f"custom_{int(time.time())}"
            
            # Use provided name or generate from ID
            if not name:
                name = f"Custom Avatar {len(self.available_avatars) + 1}"
            
            # Save image to avatars directory
            filename = f"{avatar_id}.jpg"
            filepath = os.path.join(self.avatars_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            # Add to available avatars
            avatar = {
                "id": avatar_id,
                "name": name,
                "path": filepath
            }
            
            self.available_avatars.append(avatar)
            
            # Set as current avatar
            self.avatar_image = filepath
            
            # Return avatar info for UI
            return {
                "id": avatar_id,
                "name": name,
                "thumbnail": f"/static/img/avatars/{filename}"
            }
        except Exception as e:
            print(f"Error uploading custom avatar: {e}")
            return None
    
    def get_video_for_step(self, step_text: str, step_number: int, force_regenerate: bool = False) -> Dict[str, Any]:
        """Get or generate a video for a step
        
        Args:
            step_text: Text of the step to explain
            step_number: Step number for caching
            force_regenerate: Force regeneration of video
            
        Returns:
            Dictionary with video_url and status information
        """
        if not self.initialized:
            return {
                "status": "error",
                "message": "SadTalker is not initialized",
                "video_url": None
            }
        
        if not self.avatar_image:
            return {
                "status": "error",
                "message": "No avatar image selected",
                "video_url": None
            }
        
        # Check cache first
        cache_key = f"step_{step_number}"
        if not force_regenerate and cache_key in self.video_cache:
            return {
                "status": "success",
                "video_url": self.video_cache[cache_key],
                "cached": True
            }
        
        # Generate video
        try:
            # Generate script for step
            script = self._generate_script_for_step(step_text)
            
            # Generate result file path
            result_file = os.path.join(self.cache_dir, f"step_{step_number}.mp4")
            
            # Generate video
            video_path = self.sadtalker.generate_video(
                source_image=self.avatar_image,
                text=script,
                result_file=result_file
            )
            
            if not video_path:
                return {
                    "status": "error",
                    "message": "Failed to generate video",
                    "video_url": None
                }
            
            # Convert to web URL
            video_filename = os.path.basename(video_path)
            video_url = f"/static/videos/{video_filename}"
            
            # Copy to static directory for web access
            static_videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "videos")
            os.makedirs(static_videos_dir, exist_ok=True)
            
            static_video_path = os.path.join(static_videos_dir, video_filename)
            with open(video_path, "rb") as src, open(static_video_path, "wb") as dst:
                dst.write(src.read())
            
            # Cache result
            self.video_cache[cache_key] = video_url
            
            return {
                "status": "success",
                "video_url": video_url,
                "cached": False
            }
        except Exception as e:
            print(f"Error generating video for step: {e}")
            return {
                "status": "error",
                "message": str(e),
                "video_url": None
            }
    
    def _generate_script_for_step(self, step_text: str) -> str:
        """Generate script for explaining a step
        
        Args:
            step_text: Text of the step to explain
            
        Returns:
            Script text
        """
        # For simplicity, just enhance the step text
        # In a real implementation, you could use Claude to generate better explanations
        script = f"Let me explain this step. {step_text} Make sure to follow each fold carefully. Let me know if you need any help."
        return script
    
    def get_welcome_video(self, force_regenerate: bool = False) -> Dict[str, Any]:
        """Get or generate welcome video
        
        Args:
            force_regenerate: Force regeneration of video
            
        Returns:
            Dictionary with video_url and status information
        """
        if not self.initialized:
            return {
                "status": "error",
                "message": "SadTalker is not initialized",
                "video_url": None
            }
        
        if not self.avatar_image:
            return {
                "status": "error",
                "message": "No avatar image selected",
                "video_url": None
            }
        
        # Check cache first
        cache_key = "welcome"
        if not force_regenerate and cache_key in self.video_cache:
            return {
                "status": "success",
                "video_url": self.video_cache[cache_key],
                "cached": True
            }
        
        # Generate welcome video
        try:
            # Welcome script
            script = (
                "Welcome to GuideMind! I'm your origami instructor, and I'll guide you "
                "through creating beautiful paper art step by step. You can ask me for help "
                "anytime you get stuck, or use voice commands to navigate. Let's get started!"
            )
            
            # Generate result file path
            result_file = os.path.join(self.cache_dir, "welcome.mp4")
            
            # Generate video
            video_path = self.sadtalker.generate_video(
                source_image=self.avatar_image,
                text=script,
                result_file=result_file
            )
            
            if not video_path:
                return {
                    "status": "error",
                    "message": "Failed to generate welcome video",
                    "video_url": None
                }
            
            # Convert to web URL
            video_filename = os.path.basename(video_path)
            video_url = f"/static/videos/{video_filename}"
            
            # Copy to static directory for web access
            static_videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "videos")
            os.makedirs(static_videos_dir, exist_ok=True)
            
            static_video_path = os.path.join(static_videos_dir, video_filename)
            with open(video_path, "rb") as src, open(static_video_path, "wb") as dst:
                dst.write(src.read())
            
            # Cache result
            self.video_cache[cache_key] = video_url
            
            return {
                "status": "success",
                "video_url": video_url,
                "cached": False
            }
        except Exception as e:
            print(f"Error generating welcome video: {e}")
            return {
                "status": "error",
                "message": str(e),
                "video_url": None
            }
    
    def get_help_video(self, step_text: str, force_regenerate: bool = False) -> Dict[str, Any]:
        """Get or generate help video
        
        Args:
            step_text: Text of the step needing help
            force_regenerate: Force regeneration of video
            
        Returns:
            Dictionary with video_url and status information
        """
        if not self.initialized:
            return {
                "status": "error",
                "message": "SadTalker is not initialized",
                "video_url": None
            }
        
        if not self.avatar_image:
            return {
                "status": "error",
                "message": "No avatar image selected",
                "video_url": None
            }
        
        # Check cache first
        cache_key = f"help_{step_text[:20]}"  # Use first 20 chars as part of cache key
        if not force_regenerate and cache_key in self.video_cache:
            return {
                "status": "success",
                "video_url": self.video_cache[cache_key],
                "cached": True
            }
        
        # Generate help video
        try:
            # Help script
            script = (
                f"I see you're having trouble with this step: {step_text}. "
                f"Don't worry, this is a common place to get stuck. "
                f"Try checking that your previous folds are precise, and make sure "
                f"the paper is properly aligned. Take it slowly and be gentle with the paper. "
                f"If you're still having issues, we can go back to the previous step and try again."
            )
            
            # Generate result file path
            result_file = os.path.join(self.cache_dir, f"help_{int(time.time())}.mp4")
            
            # Generate video
            video_path = self.sadtalker.generate_video(
                source_image=self.avatar_image,
                text=script,
                result_file=result_file
            )
            
            if not video_path:
                return {
                    "status": "error",
                    "message": "Failed to generate help video",
                    "video_url": None
                }
            
            # Convert to web URL
            video_filename = os.path.basename(video_path)
            video_url = f"/static/videos/{video_filename}"
            
            # Copy to static directory for web access
            static_videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "videos")
            os.makedirs(static_videos_dir, exist_ok=True)
            
            static_video_path = os.path.join(static_videos_dir, video_filename)
            with open(video_path, "rb") as src, open(static_video_path, "wb") as dst:
                dst.write(src.read())
            
            # Cache result
            self.video_cache[cache_key] = video_url
            
            return {
                "status": "success",
                "video_url": video_url,
                "cached": False
            }
        except Exception as e:
            print(f"Error generating help video: {e}")
            return {
                "status": "error",
                "message": str(e),
                "video_url": None
            }
    
    def add_sample_avatars(self) -> List[Dict[str, str]]:
        """Add sample avatar images if none are available
        
        Returns:
            List of added avatar dictionaries
        """
        if self.available_avatars:
            # Already have avatars
            return []
        
        added_avatars = []
        
        try:
            # Sample avatar URLs
            sample_avatars = [
                {
                    "id": "professional_male",
                    "name": "Professional Male",
                    "url": "https://thispersondoesnotexist.com/"
                },
                {
                    "id": "professional_female",
                    "name": "Professional Female",
                    "url": "https://thispersondoesnotexist.com/"
                }
            ]
            
            for avatar in sample_avatars:
                try:
                    # Download avatar image
                    response = requests.get(avatar["url"], stream=True)
                    if response.status_code == 200:
                        # Save to avatars directory
                        filename = f"{avatar['id']}.jpg"
                        filepath = os.path.join(self.avatars_dir, filename)
                        
                        with open(filepath, "wb") as f:
                            response.raw.decode_content = True
                            f.write(response.raw.read())
                        
                        # Add to available avatars
                        avatar_dict = {
                            "id": avatar["id"],
                            "name": avatar["name"],
                            "path": filepath
                        }
                        
                        self.available_avatars.append(avatar_dict)
                        added_avatars.append({
                            "id": avatar["id"],
                            "name": avatar["name"],
                            "thumbnail": f"/static/img/avatars/{filename}"
                        })
                        
                        # Set as default avatar if none selected
                        if not self.avatar_image:
                            self.avatar_image = filepath
                except Exception as e:
                    print(f"Error downloading sample avatar {avatar['id']}: {e}")
        except Exception as e:
            print(f"Error adding sample avatars: {e}")
        
        return added_avatars

# Create controller instance
sadtalker_controller = SadTalkerController()