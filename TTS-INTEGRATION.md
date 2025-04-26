# Integrating Azure or Google TTS with GuideMind

This guide explains how to enhance GuideMind with professional Text-to-Speech (TTS) services from Azure or Google for your hackathon presentation.

## Azure Text-to-Speech Integration

### Setup

1. Sign up for [Azure Speech Services](https://azure.microsoft.com/en-us/services/cognitive-services/speech-services/)
2. Create a Speech resource in the Azure portal
3. Get your subscription key and region

### Integration in JavaScript

Replace the browser's speech synthesis with Azure TTS by modifying the `speakText` function in `static/js/main.js`:

```javascript
// Add these near the top of the file
const azureKey = "YOUR_AZURE_SUBSCRIPTION_KEY"; 
const azureRegion = "YOUR_REGION";

// Replace the speakText function with this version
function speakText(text) {
    // Show speaking indicator and animate avatar
    $('.speaking-indicator').removeClass('d-none');
    
    // Switch avatar video to speaking version
    try {
        const videoElement = document.getElementById('avatar-video');
        const speakingVideoUrl = '/static/video/avatar-speaking.mp4';
        
        if (videoElement) {
            $('#avatar-video-source').attr('src', speakingVideoUrl);
            videoElement.load();
            videoElement.play().catch(e => console.log('Video play error:', e));
        }
    } catch (e) {
        console.error('Avatar video error:', e);
    }
    
    // Azure TTS implementation
    const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(azureKey, azureRegion);
    speechConfig.speechSynthesisVoiceName = "en-US-JennyNeural"; // Or any other Azure voice
    
    const audioConfig = SpeechSDK.AudioConfig.fromDefaultSpeakerOutput();
    const synthesizer = new SpeechSDK.SpeechSynthesizer(speechConfig, audioConfig);
    
    synthesizer.speakTextAsync(
        text,
        result => {
            if (result) {
                synthesizer.close();
                
                // Return to idle video when done speaking
                try {
                    const videoElement = document.getElementById('avatar-video');
                    const idleVideoUrl = '/static/video/avatar-idle.mp4';
                    
                    if (videoElement) {
                        $('#avatar-video-source').attr('src', idleVideoUrl);
                        videoElement.load();
                        videoElement.play().catch(e => console.log('Video play error:', e));
                    }
                } catch (e) {
                    console.error('Avatar video error:', e);
                }
                
                $('.speaking-indicator').addClass('d-none');
            }
        },
        error => {
            console.log(error);
            synthesizer.close();
            $('.speaking-indicator').addClass('d-none');
        });
}
```

Also add the Azure SDK to your HTML:

```html
<script src="https://aka.ms/csspeech/jsbrowserpackageraw"></script>
```

## Google Cloud Text-to-Speech Integration

### Setup

1. Create a [Google Cloud Platform](https://cloud.google.com/) account
2. Enable the Cloud Text-to-Speech API
3. Create an API key

### Integration Method

For a hackathon demo, the simplest approach is to pre-generate audio files for each step:

1. Use Google's TTS API to generate MP3 files for each origami step
2. Place these in `/static/audio/step-1.mp3`, `/static/audio/step-2.mp3`, etc.
3. Modify the speakText function to play these files:

```javascript
function speakText(text, stepNumber) {
    // Show speaking indicator and animate avatar
    $('.speaking-indicator').removeClass('d-none');
    
    // Switch avatar video to speaking version
    try {
        const videoElement = document.getElementById('avatar-video');
        const speakingVideoUrl = '/static/video/avatar-speaking.mp4';
        
        if (videoElement) {
            $('#avatar-video-source').attr('src', speakingVideoUrl);
            videoElement.load();
            videoElement.play().catch(e => console.log('Video play error:', e));
        }
    } catch (e) {
        console.error('Avatar video error:', e);
    }
    
    // Play pre-generated audio file
    const audio = new Audio(`/static/audio/step-${stepNumber}.mp3`);
    
    audio.onended = function() {
        // Return to idle video when done speaking
        try {
            const videoElement = document.getElementById('avatar-video');
            const idleVideoUrl = '/static/video/avatar-idle.mp4';
            
            if (videoElement) {
                $('#avatar-video-source').attr('src', idleVideoUrl);
                videoElement.load();
                videoElement.play().catch(e => console.log('Video play error:', e));
            }
        } catch (e) {
            console.error('Avatar video error:', e);
        }
        
        $('.speaking-indicator').addClass('d-none');
    };
    
    audio.play();
}
```

## Hackathon Demo Tip

For the hackathon demo, you might not have time to fully implement the API integrations. Instead:

1. Pre-record the voice narrations for each step using either service
2. Save them as MP3 files in `/static/audio/`
3. Use the simplified method above to play the pre-recorded audio in sync with the avatar video

This approach allows you to showcase high-quality voice narration without live API calls.