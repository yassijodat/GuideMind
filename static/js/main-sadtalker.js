$(document).ready(function() {
    // State variables
    let totalSteps = 0;
    let currentStep = 0;
    let currentAudio = null;
    let lastExplanation = '';
    let isListening = false;
    let recognition = null;

    // Initialize speech synthesis
    const synth = window.speechSynthesis;
    
    // Initialize speech recognition if available
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        // Handle recognition results
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript.toLowerCase();
            console.log('Voice input:', transcript);
            
            // Check for keywords
            if (transcript.includes('stuck') || transcript.includes('help') || 
                transcript.includes('don\'t understand') || transcript.includes('confused')) {
                $('#help-button').click();
            } else if (transcript.includes('next') || transcript.includes('continue')) {
                $('#next-step').click();
            } else if (transcript.includes('back') || transcript.includes('previous')) {
                $('#prev-step').click();
            } else if (transcript.includes('repeat') || transcript.includes('again')) {
                $('#replay-audio').click();
            }
        };
        
        recognition.onend = function() {
            isListening = false;
            $('#voice-indicator').removeClass('listening').html('<i class="fas fa-microphone"></i> Voice Control');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            isListening = false;
            $('#voice-indicator').removeClass('listening').html('<i class="fas fa-microphone"></i> Voice Control');
        };
    }
    
    // Handle upload form submission
    $('#upload-form').on('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('manual-upload');
        if (fileInput.files.length === 0) {
            alert('Please select a file first.');
            return;
        }
        
        const formData = new FormData();
        formData.append('manual', fileInput.files[0]);
        
        $.ajax({
            url: '/load-instructions',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: handleInstructionsLoaded,
            error: function() {
                alert('Error loading instructions. Please try again.');
            }
        });
    });
    
    // Handle preloaded instruction selection
    $('#preloaded-crane').on('click', function() {
        $.ajax({
            url: '/load-instructions',
            type: 'POST',
            data: {
                preloaded_key: 'basic_crane'
            },
            success: handleInstructionsLoaded,
            error: function() {
                alert('Error loading instructions. Please try again.');
            }
        });
    });
    
    // Handle instructions loaded
    async function handleInstructionsLoaded(data) {
        if (data.success) {
            totalSteps = data.total_steps;
            currentStep = 0;
            
            // Show guide interface
            $('#setup-container').hide();
            $('#guide-container').show();
            
            // Try to show welcome video with avatar system if available
            let showingWelcome = false;
            
            if (typeof avatarManager !== 'undefined' && await avatarManager.initialize()) {
                try {
                    // Show loading indicator
                    $('.speaking-indicator').removeClass('d-none').text('Generating welcome...');
                    
                    // Get welcome video
                    const welcomeVideoUrl = await avatarManager.getWelcomeVideo();
                    
                    if (welcomeVideoUrl) {
                        // Update the video source
                        const videoElement = document.getElementById('avatar-video');
                        if (videoElement) {
                            // Set onended event to load the first step when welcome is done
                            videoElement.onended = function() {
                                $('.speaking-indicator').addClass('d-none');
                                
                                // Now load the first step
                                loadStep(0);
                            };
                            
                            // Set video source and play
                            videoElement.src = welcomeVideoUrl;
                            videoElement.load();
                            videoElement.play().catch(e => {
                                console.error('Error playing welcome video:', e);
                                
                                // Fallback to loading first step directly
                                loadStep(0);
                            });
                            
                            showingWelcome = true;
                            
                            // Show the speaking indicator
                            $('.speaking-indicator').text('Speaking...').removeClass('d-none');
                        }
                    }
                } catch (error) {
                    console.error('Error showing welcome video:', error);
                }
            }
            
            // If not showing welcome video, load first step directly
            if (!showingWelcome) {
                loadStep(0);
            }
        } else {
            alert('Error: ' + data.error);
        }
    }
    
    // Load a specific step
    function loadStep(stepNumber) {
        $.ajax({
            url: '/get-step',
            type: 'GET',
            data: {
                step: stepNumber
            },
            success: async function(data) {
                if (data.success) {
                    currentStep = stepNumber;
                    
                    // Update UI
                    $('#step-title').text('Step ' + data.step_number);
                    $('#step-instruction').text(data.instruction);
                    $('#step-explanation').html(data.explanation);
                    
                    // Update progress bar
                    const progress = (data.step_number / data.total_steps) * 100;
                    $('.progress-bar').css('width', progress + '%');
                    $('.progress-bar').attr('aria-valuenow', progress);
                    $('.progress-bar').text(`Step ${data.step_number}/${data.total_steps}`);
                    
                    // Try to use the avatar video system if available
                    let usingAvatarVideo = false;
                    
                    if (typeof avatarManager !== 'undefined' && await avatarManager.initialize()) {
                        try {
                            // Show loading indicator
                            $('.speaking-indicator').removeClass('d-none').text('Generating avatar...');
                            
                            // Get video for this step
                            const videoUrl = await avatarManager.getStepVideo(stepNumber);
                            
                            if (videoUrl) {
                                // Update the video source
                                const videoElement = document.getElementById('avatar-video');
                                if (videoElement) {
                                    // Set onended event to hide speaking indicator
                                    videoElement.onended = function() {
                                        $('.speaking-indicator').addClass('d-none');
                                    };
                                    
                                    // Set video source and play
                                    videoElement.src = videoUrl;
                                    videoElement.load();
                                    videoElement.play().catch(e => {
                                        console.error('Error playing avatar video:', e);
                                        
                                        // Fallback to regular speech
                                        speakText(data.explanation);
                                    });
                                    
                                    // Mark as using avatar video
                                    usingAvatarVideo = true;
                                    
                                    // Show the speaking indicator
                                    $('.speaking-indicator').text('Speaking...').removeClass('d-none');
                                }
                            }
                        } catch (error) {
                            console.error('Error using avatar for step explanation:', error);
                        }
                    }
                    
                    // If not using avatar video, use regular speech synthesis
                    if (!usingAvatarVideo) {
                        speakText(data.explanation);
                    }
                    
                    lastExplanation = data.explanation;
                    
                    // Hide troubleshooting if visible
                    $('#troubleshooting-container').hide();
                    
                    // Enable/disable navigation buttons
                    if (currentStep === 0) {
                        $('#prev-step').prop('disabled', true);
                    } else {
                        $('#prev-step').prop('disabled', false);
                    }
                    
                    if (currentStep === totalSteps - 1) {
                        $('#next-step').text('Finish');
                    } else {
                        $('#next-step').text('Next Step');
                    }
                } else {
                    alert('Error: ' + data.error);
                    
                    if (data.is_complete) {
                        showCompletion();
                    }
                }
            },
            error: function() {
                alert('Error loading step. Please try again.');
            }
        });
    }
    
    // Handle next step button
    $('#next-step').on('click', function() {
        if (currentStep === totalSteps - 1) {
            showCompletion();
        } else {
            $.ajax({
                url: '/next-step',
                type: 'POST',
                success: function(data) {
                    if (data.success) {
                        loadStep(currentStep + 1);
                    } else {
                        if (data.is_complete) {
                            showCompletion();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    }
                },
                error: function() {
                    alert('Error navigating to next step. Please try again.');
                }
            });
        }
    });
    
    // Handle previous step button
    $('#prev-step').on('click', function() {
        $.ajax({
            url: '/previous-step',
            type: 'POST',
            success: function(data) {
                if (data.success) {
                    loadStep(currentStep - 1);
                } else {
                    alert('Error: ' + data.error);
                }
            },
            error: function() {
                alert('Error navigating to previous step. Please try again.');
            }
        });
    });
    
    // Handle help button
    $('#help-button').on('click', function() {
        $.ajax({
            url: '/troubleshoot',
            type: 'GET',
            success: async function(data) {
                if (data.success) {
                    $('#troubleshooting-content').html(data.troubleshooting);
                    $('#troubleshooting-container').show();
                    
                    // Try to use avatar system if available
                    let usingAvatarVideo = false;
                    
                    if (typeof avatarManager !== 'undefined' && await avatarManager.initialize()) {
                        try {
                            // Show loading indicator
                            $('.speaking-indicator').removeClass('d-none').text('Generating help...');
                            
                            // Get current step
                            const currentStepText = $('#step-instruction').text();
                            
                            // Get help video
                            const videoUrl = await avatarManager.getHelpVideo(currentStepText);
                            
                            if (videoUrl) {
                                // Update the video source
                                const videoElement = document.getElementById('avatar-video');
                                if (videoElement) {
                                    // Set onended event to hide speaking indicator
                                    videoElement.onended = function() {
                                        $('.speaking-indicator').addClass('d-none');
                                    };
                                    
                                    // Set video source and play
                                    videoElement.src = videoUrl;
                                    videoElement.load();
                                    videoElement.play().catch(e => {
                                        console.error('Error playing avatar video:', e);
                                        
                                        // Fallback to regular speech
                                        speakText(data.troubleshooting);
                                    });
                                    
                                    // Mark as using avatar video
                                    usingAvatarVideo = true;
                                    
                                    // Show the speaking indicator
                                    $('.speaking-indicator').text('Speaking...').removeClass('d-none');
                                }
                            }
                        } catch (error) {
                            console.error('Error using avatar for troubleshooting:', error);
                        }
                    }
                    
                    // If not using avatar video, use regular speech synthesis
                    if (!usingAvatarVideo) {
                        speakText(data.troubleshooting);
                    }
                } else {
                    alert('Error: ' + data.error);
                }
            },
            error: function() {
                alert('Error getting troubleshooting advice. Please try again.');
            }
        });
    });
    
    // Handle close troubleshooting button
    $('#close-troubleshooting').on('click', function() {
        $('#troubleshooting-container').hide();
        
        // Stop speaking if currently speaking troubleshooting
        if (currentAudio) {
            synth.cancel();
            $('.speaking-indicator').addClass('d-none');
            currentAudio = null;
        }
    });
    
    // Handle replay audio button
    $('#replay-audio').on('click', function() {
        if (lastExplanation) {
            speakText(lastExplanation);
        }
    });
    
    // Handle restart button
    $('#restart-button').on('click', function() {
        $('#completion-container').hide();
        $('#setup-container').show();
        
        // Reset state
        totalSteps = 0;
        currentStep = 0;
    });
    
    // Add voice control button functionality
    $('#voice-indicator').on('click', function() {
        if (!recognition) {
            alert('Speech recognition is not supported in your browser. Please try Chrome.');
            return;
        }
        
        if (!isListening) {
            // Start listening
            recognition.start();
            isListening = true;
            $(this).addClass('listening').html('<i class="fas fa-microphone"></i> Listening...');
        } else {
            // Stop listening
            recognition.stop();
            isListening = false;
            $(this).removeClass('listening').html('<i class="fas fa-microphone"></i> Voice Control');
        }
    });
    
    // Text-to-speech function
    function speakText(text) {
        // Stop any current speech
        if (synth.speaking) {
            synth.cancel();
        }
        
        // Clean up the text (remove HTML tags and simplify)
        const cleanText = text
            .replace(/<[^>]*>/g, '')  // Remove HTML tags
            .replace(/\s+/g, ' ')      // Normalize whitespace
            .trim();
        
        // Create speech utterance
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.9;  // Slightly slower than default
        utterance.pitch = 1;
        
        // Find a good voice (preferably female English voice)
        const voices = synth.getVoices();
        const preferredVoice = voices.find(voice => 
            voice.name.includes('Google') && 
            voice.name.includes('Female') && 
            voice.lang.includes('en-')
        ) || voices.find(voice => 
            voice.lang.includes('en-')
        ) || voices[0];
        
        if (preferredVoice) {
            utterance.voice = preferredVoice;
        }
        
        // Show speaking indicator
        $('.speaking-indicator').removeClass('d-none').text('Speaking...');
        
        // Event handlers
        utterance.onend = function() {
            $('.speaking-indicator').addClass('d-none');
            currentAudio = null;
        };
        
        utterance.onerror = function() {
            $('.speaking-indicator').addClass('d-none');
            currentAudio = null;
            console.error('Speech synthesis error');
        };
        
        // Speak
        synth.speak(utterance);
        currentAudio = utterance;
    }
    
    // Show completion screen
    function showCompletion() {
        $('#guide-container').hide();
        $('#completion-container').show();
        
        // Speak congratulations
        speakText("Congratulations! You've completed all the steps!");
    }
    
    // Handle voices loading (Chrome needs this)
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = function() {
            // Voices loaded
        };
    }
});