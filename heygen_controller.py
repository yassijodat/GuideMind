import os
import json
import time
from flask import Flask, jsonify, request
from heygen_integration import HeyGenAPI

class HeyGenController:
    """Controller for managing HeyGen video avatar integration with GuideMind"""
    
    def __init__(self):
        self.heygen = HeyGenAPI()
        self.initialized = False
        self.avatar_id = None
        self.voice_id = None
        self.avatar_cache = {}  # Cache for generated videos
        self.available_avatars = []
        self.available_voices = []
    
    def initialize(self):
        """Initialize HeyGen controller and fetch available resources"""
        if self.initialized:
            return True
            
        if not self.heygen.is_authenticated():
            print("Error: HeyGen API authentication failed")
            return False
        
        # Fetch available avatars and voices
        self.available_avatars = self.heygen.list_avatars()
        self.available_voices = self.heygen.list_voices()
        
        if not self.available_avatars:
            print("Error: No avatars available in HeyGen account")
            return False
        
        # Set default avatar and voice
        self.avatar_id = self.available_avatars[0].get("avatar_id")
        
        # Find a suitable voice (prefer English voices)
        for voice in self.available_voices:
            if voice.get("language", "").lower() == "english":
                self.voice_id = voice.get("voice_id")
                break
        
        # If no English voice found, use the first available voice
        if not self.voice_id and self.available_voices:
            self.voice_id = self.available_voices[0].get("voice_id")
        
        self.initialized = True
        return True
    
    def get_avatar_options(self):
        """Get available avatar options for UI selection"""
        if not self.initialized:
            if not self.initialize():
                return []
        
        return [
            {
                "id": avatar.get("avatar_id"),
                "name": avatar.get("name", "Unknown"),
                "thumbnail": avatar.get("portrait_url", "")
            }
            for avatar in self.available_avatars
        ]
    
    def get_voice_options(self):
        """Get available voice options for UI selection"""
        if not self.initialized:
            if not self.initialize():
                return []
        
        return [
            {
                "id": voice.get("voice_id"),
                "name": voice.get("name", "Unknown"),
                "language": voice.get("language", "Unknown")
            }
            for voice in self.available_voices
        ]
    
    def set_avatar(self, avatar_id):
        """Set the avatar to use for video generation"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        # Verify avatar_id is valid
        for avatar in self.available_avatars:
            if avatar.get("avatar_id") == avatar_id:
                self.avatar_id = avatar_id
                return True
        
        return False
    
    def set_voice(self, voice_id):
        """Set the voice to use for video generation"""
        if not self.initialized:
            if not self.initialize():
                return False
        
        # Verify voice_id is valid
        for voice in self.available_voices:
            if voice.get("voice_id") == voice_id:
                self.voice_id = voice_id
                return True
        
        return False
    
    def get_video_for_step(self, step_text, step_number, force_regenerate=False):
        """Get or generate a video for the given step
        
        Args:
            step_text: The text of the step to explain
            step_number: The step number for caching
            force_regenerate: Force regeneration even if cached
            
        Returns:
            Dictionary with video_url and status or error message
        """
        if not self.initialized:
            if not self.initialize():
                return {"error": "HeyGen API not initialized", "status": "error"}
        
        # Check cache first unless force_regenerate is True
        cache_key = f"step_{step_number}"
        if not force_regenerate and cache_key in self.avatar_cache:
            return {
                "video_url": self.avatar_cache[cache_key],
                "status": "success",
                "cached": True
            }
        
        # No cached video, generate a new one
        if not self.avatar_id:
            return {"error": "No avatar selected", "status": "error"}
        
        # Generate script with enhanced step explanation
        script = self._generate_script_for_step(step_text)
        
        # Generate video
        video_url = self.heygen.generate_video(
            avatar_id=self.avatar_id,
            script=script,
            voice_id=self.voice_id
        )
        
        if not video_url:
            return {"error": "Failed to generate video", "status": "error"}
        
        # Cache the result
        self.avatar_cache[cache_key] = video_url
        
        return {
            "video_url": video_url,
            "status": "success",
            "cached": False
        }
    
    def _generate_script_for_step(self, step_text):
        """Generate a script for the avatar to explain a step
        
        Args:
            step_text: The text of the step to explain
            
        Returns:
            A script for the avatar to say
        """
        # For now, a simple enhancement of the step text
        # In a full implementation, you might use Claude API to generate a better explanation
        return f"Let me explain this step. {step_text} Make sure to align the folds carefully. Take your time with this step."
    
    def get_welcome_video(self, force_regenerate=False):
        """Generate a welcome video for the application
        
        Returns:
            Dictionary with video_url and status or error message
        """
        if not self.initialized:
            if not self.initialize():
                return {"error": "HeyGen API not initialized", "status": "error"}
        
        # Check cache first unless force_regenerate is True
        cache_key = "welcome"
        if not force_regenerate and cache_key in self.avatar_cache:
            return {
                "video_url": self.avatar_cache[cache_key],
                "status": "success",
                "cached": True
            }
        
        # Generate welcome video
        script = (
            "Welcome to GuideMind! I'm your origami instructor, and I'll guide you "
            "through creating beautiful paper art step by step. You can ask me for help "
            "anytime you get stuck, or use voice commands to navigate. Let's get started!"
        )
        
        video_url = self.heygen.generate_video(
            avatar_id=self.avatar_id,
            script=script,
            voice_id=self.voice_id
        )
        
        if not video_url:
            return {"error": "Failed to generate welcome video", "status": "error"}
        
        # Cache the result
        self.avatar_cache[cache_key] = video_url
        
        return {
            "video_url": video_url,
            "status": "success",
            "cached": False
        }
    
    def get_help_video(self, step_text, force_regenerate=False):
        """Generate a help video for when user is stuck
        
        Args:
            step_text: The text of the step they're stuck on
            
        Returns:
            Dictionary with video_url and status or error message
        """
        if not self.initialized:
            if not self.initialize():
                return {"error": "HeyGen API not initialized", "status": "error"}
        
        # Check cache first unless force_regenerate is True
        cache_key = f"help_{step_text[:20]}"  # Use first 20 chars of step as cache key
        if not force_regenerate and cache_key in self.avatar_cache:
            return {
                "video_url": self.avatar_cache[cache_key],
                "status": "success",
                "cached": True
            }
        
        # Generate help script
        script = (
            f"I see you're having trouble with this step: {step_text}. "
            f"Don't worry, this is a common place to get stuck. "
            f"Try checking that your previous folds are precise, and make sure "
            f"the paper is properly aligned. Take it slowly and be gentle with the paper. "
            f"If you're still having issues, we can go back to the previous step and try again."
        )
        
        video_url = self.heygen.generate_video(
            avatar_id=self.avatar_id,
            script=script,
            voice_id=self.voice_id
        )
        
        if not video_url:
            return {"error": "Failed to generate help video", "status": "error"}
        
        # Cache the result
        self.avatar_cache[cache_key] = video_url
        
        return {
            "video_url": video_url,
            "status": "success",
            "cached": False
        }

# Create singleton instance
heygen_controller = HeyGenController()