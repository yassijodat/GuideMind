// SadTalker integration for GuideMind

class AvatarManager {
    constructor() {
        this.initialized = false;
        this.avatars = [];
        this.selectedAvatarId = null;
        this.videos = {};  // Cache for video URLs
    }

    async initialize() {
        if (this.initialized) {
            return true;
        }

        try {
            // Check if SadTalker is available
            const statusResponse = await fetch('/api/avatar/status');
            const statusData = await statusResponse.json();

            if (statusData.status !== 'success' || !statusData.initialized) {
                console.error('Avatar system not initialized:', statusData.message);
                return false;
            }

            // Fetch available avatars
            const avatarsResponse = await fetch('/api/avatar/options');
            const avatarsData = await avatarsResponse.json();

            if (avatarsData.status === 'success' && avatarsData.avatars?.length > 0) {
                this.avatars = avatarsData.avatars;
                this.selectedAvatarId = this.avatars[0].id;
            } else {
                console.warn('No avatars available');
            }

            this.initialized = true;
            console.log('Avatar system initialized successfully');
            return true;
        } catch (error) {
            console.error('Error initializing avatar system:', error);
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

        if (this.avatars.length === 0) {
            container.html('<div class="alert alert-warning">No avatars available. Upload your own image below.</div>');
            return;
        }

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

    async setAvatar(avatarId) {
        try {
            const response = await fetch('/api/avatar/set', {
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

    async uploadAvatar(formData) {
        try {
            const response = await fetch('/api/avatar/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Add new avatar to list
                this.avatars.push(data.avatar);
                this.selectedAvatarId = data.avatar.id;
                
                console.log('Avatar uploaded successfully:', data.avatar);
                return data.avatar;
            } else {
                console.error('Failed to upload avatar:', data.message);
                return null;
            }
        } catch (error) {
            console.error('Error uploading avatar:', error);
            return null;
        }
    }

    async getWelcomeVideo(forceRegenerate = false) {
        try {
            const response = await fetch(`/api/avatar/welcome-video?force=${forceRegenerate}`);
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
            
            const response = await fetch(`/api/avatar/step-video/${stepNumber}?force=${forceRegenerate}`);
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
            const response = await fetch(`/api/avatar/help-video?force=${forceRegenerate}`, {
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
const avatarManager = new AvatarManager();

// Initialize on page load
$(document).ready(async function() {
    if (await avatarManager.initialize()) {
        // Update UI to show avatar system is available
        $('#avatar-status').text('Avatars Available').addClass('text-success');
        
        // Setup avatar selector if it exists
        if ($('#avatar-selector').length) {
            await avatarManager.populateAvatarSelector('#avatar-selector');
        }
        
        // Setup avatar upload form if it exists
        if ($('#avatar-upload-form').length) {
            $('#avatar-upload-form').on('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                
                // Show loading indicator
                $('#avatar-upload-status').html('<div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Uploading...</span></div> Uploading avatar...');
                
                const avatar = await avatarManager.uploadAvatar(formData);
                
                if (avatar) {
                    $('#avatar-upload-status').html('<div class="alert alert-success">Avatar uploaded successfully!</div>');
                    
                    // Refresh avatar selector
                    if ($('#avatar-selector').length) {
                        await avatarManager.populateAvatarSelector('#avatar-selector');
                    }
                } else {
                    $('#avatar-upload-status').html('<div class="alert alert-danger">Failed to upload avatar.</div>');
                }
            });
            
            // Show image preview when file is selected
            $('#avatar-image').on('change', function() {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        $('#avatar-preview').attr('src', e.target.result).show();
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    } else {
        // Update UI to show avatar system is not available
        $('#avatar-status').text('Avatars Not Available').addClass('text-danger');
    }
});