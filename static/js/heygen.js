// HeyGen integration for GuideMind

class HeyGenManager {
    constructor() {
        this.initialized = false;
        this.avatars = [];
        this.voices = [];
        this.selectedAvatarId = null;
        this.selectedVoiceId = null;
        this.videos = {};  // Cache for video URLs
    }

    async initialize() {
        if (this.initialized) {
            return true;
        }

        try {
            // Check if HeyGen API is available
            const statusResponse = await fetch('/api/heygen/status');
            const statusData = await statusResponse.json();

            if (statusData.status !== 'success' || !statusData.initialized) {
                console.error('HeyGen API not initialized:', statusData.message);
                return false;
            }

            // Fetch available avatars
            const avatarsResponse = await fetch('/api/heygen/avatars');
            const avatarsData = await avatarsResponse.json();

            if (avatarsData.status === 'success' && avatarsData.avatars?.length > 0) {
                this.avatars = avatarsData.avatars;
                this.selectedAvatarId = this.avatars[0].id;
            } else {
                console.error('No HeyGen avatars available');
                return false;
            }

            // Fetch available voices
            const voicesResponse = await fetch('/api/heygen/voices');
            const voicesData = await voicesResponse.json();

            if (voicesData.status === 'success' && voicesData.voices?.length > 0) {
                this.voices = voicesData.voices;
                
                // Try to find an English voice
                const englishVoice = this.voices.find(voice => 
                    voice.language?.toLowerCase().includes('english'));
                
                this.selectedVoiceId = englishVoice ? englishVoice.id : this.voices[0].id;
            } else {
                console.error('No HeyGen voices available');
                return false;
            }

            this.initialized = true;
            console.log('HeyGen API initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing HeyGen:', error);
            return false;
        }
    }

    async populateAvatarSelector(selector) {
        if (!this.initialized) {
            await this.initialize();
        }

        const container = $(selector);
        if (!container.length) {
            console.error('Avatar selector container not found:', selector);
            return;
        }

        container.empty();

        // Add avatar options
        this.avatars.forEach(avatar => {
            const option = $(`
                <div class="avatar-option ${avatar.id === this.selectedAvatarId ? 'selected' : ''}" 
                     data-avatar-id="${avatar.id}">
                    <img src="${avatar.thumbnail || '/static/img/avatar-placeholder.jpg'}" 
                         alt="${avatar.name}" class="avatar-thumbnail">
                    <span>${avatar.name}</span>
                </div>
            `);
            container.append(option);
        });

        // Add click event to select avatar
        container.on('click', '.avatar-option', async (e) => {
            const avatarId = $(e.currentTarget).data('avatar-id');
            
            // Update UI
            container.find('.avatar-option').removeClass('selected');
            $(e.currentTarget).addClass('selected');
            
            // Set avatar in backend
            await this.setAvatar(avatarId);
        });
    }

    async populateVoiceSelector(selector) {
        if (!this.initialized) {
            await this.initialize();
        }

        const container = $(selector);
        if (!container.length) {
            console.error('Voice selector container not found:', selector);
            return;
        }

        container.empty();

        // Group voices by language
        const voicesByLanguage = {};
        this.voices.forEach(voice => {
            const language = voice.language || 'Unknown';
            if (!voicesByLanguage[language]) {
                voicesByLanguage[language] = [];
            }
            voicesByLanguage[language].push(voice);
        });

        // Create option groups by language
        Object.keys(voicesByLanguage).sort().forEach(language => {
            const optgroup = $(`<optgroup label="${language}"></optgroup>`);
            
            voicesByLanguage[language].forEach(voice => {
                const option = $(`<option value="${voice.id}" ${voice.id === this.selectedVoiceId ? 'selected' : ''}>${voice.name}</option>`);
                optgroup.append(option);
            });
            
            container.append(optgroup);
        });

        // Add change event to select voice
        container.on('change', async (e) => {
            const voiceId = $(e.target).val();
            await this.setVoice(voiceId);
        });
    }

    async setAvatar(avatarId) {
        try {
            const response = await fetch('/api/heygen/set-avatar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ avatar_id: avatarId })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.selectedAvatarId = avatarId;
                console.log('Avatar set successfully:', avatarId);
                return true;
            } else {
                console.error('Failed to set avatar:', data.message);
                return false;
            }
        } catch (error) {
            console.error('Error setting avatar:', error);
            return false;
        }
    }

    async setVoice(voiceId) {
        try {
            const response = await fetch('/api/heygen/set-voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ voice_id: voiceId })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.selectedVoiceId = voiceId;
                console.log('Voice set successfully:', voiceId);
                return true;
            } else {
                console.error('Failed to set voice:', data.message);
                return false;
            }
        } catch (error) {
            console.error('Error setting voice:', error);
            return false;
        }
    }

    async getWelcomeVideo(forceRegenerate = false) {
        try {
            const response = await fetch(`/api/heygen/welcome-video?force=${forceRegenerate}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.videos.welcome = data.video_url;
                return data.video_url;
            } else {
                console.error('Failed to get welcome video:', data.message);
                return null;
            }
        } catch (error) {
            console.error('Error getting welcome video:', error);
            return null;
        }
    }

    async getStepVideo(stepNumber, forceRegenerate = false) {
        try {
            const cacheKey = `step_${stepNumber}`;
            
            // Return cached video if available
            if (!forceRegenerate && this.videos[cacheKey]) {
                return this.videos[cacheKey];
            }
            
            const response = await fetch(`/api/heygen/step-video/${stepNumber}?force=${forceRegenerate}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.videos[cacheKey] = data.video_url;
                return data.video_url;
            } else {
                console.error(`Failed to get video for step ${stepNumber}:`, data.message);
                return null;
            }
        } catch (error) {
            console.error(`Error getting video for step ${stepNumber}:`, error);
            return null;
        }
    }

    async getHelpVideo(stepText, forceRegenerate = false) {
        try {
            const response = await fetch(`/api/heygen/help-video?force=${forceRegenerate}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ step_text: stepText })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data.video_url;
            } else {
                console.error('Failed to get help video:', data.message);
                return null;
            }
        } catch (error) {
            console.error('Error getting help video:', error);
            return null;
        }
    }

    // Utility method to play video in a specific element
    playVideo(videoUrl, elementId, onEnded = null) {
        const videoElement = document.getElementById(elementId);
        if (!videoElement) {
            console.error('Video element not found:', elementId);
            return false;
        }
        
        // Set video source
        videoElement.src = videoUrl;
        
        // Add end event handler if provided
        if (onEnded) {
            videoElement.onended = onEnded;
        }
        
        // Play video
        videoElement.load();
        videoElement.play().catch(error => {
            console.error('Error playing video:', error);
        });
        
        return true;
    }
}

// Create singleton instance
const heygenManager = new HeyGenManager();

// Initialize on page load
$(document).ready(async function() {
    if (await heygenManager.initialize()) {
        // Update UI to show HeyGen is available
        $('#heygen-status').text('HeyGen Connected').addClass('text-success');
        
        // Setup avatar and voice selectors if they exist
        if ($('#avatar-selector').length) {
            await heygenManager.populateAvatarSelector('#avatar-selector');
        }
        
        if ($('#voice-selector').length) {
            await heygenManager.populateVoiceSelector('#voice-selector');
        }
    } else {
        // Update UI to show HeyGen is not available
        $('#heygen-status').text('HeyGen Not Available').addClass('text-danger');
    }
});