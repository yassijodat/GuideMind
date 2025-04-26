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
            $('#voice-indicator').removeClass('listening').text('Voice Control');
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            isListening = false;
            $('#voice-indicator').removeClass('listening').text('Voice Control');
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

    // Handle Easy Dragon selection
    $('#preloaded-dragon').on('click', function() {
        $.ajax({
            url: '/load-instructions',
            type: 'POST',
            data: {
                preloaded_key: 'easy_dragon'
            },
            success: handleInstructionsLoaded,
            error: function() {
                alert('Error loading instructions. Please try again.');
            }
        });
    });

    // Handle Jumping Frog selection
    $('#preloaded-frog').on('click', function() {
        $.ajax({
            url: '/load-instructions',
            type: 'POST',
            data: {
                preloaded_key: 'jumping_frog'
            },
            success: handleInstructionsLoaded,
            error: function() {
                alert('Error loading instructions. Please try again.');
            }
        });
    });

    // Handle Lotus Flower selection
    $('#preloaded-lotus').on('click', function() {
        $.ajax({
            url: '/load-instructions',
            type: 'POST',
            data: {
                preloaded_key: 'lotus_flower'
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
            
            // Try to show welcome video with HeyGen if available
            let showingWelcome = false;
            
            if (typeof heygenManager !== 'undefined' && await heygenManager.initialize()) {
                try {
                    // Show loading indicator
                    $('.speaking-indicator').removeClass('d-none').text('Generating welcome...');
                    
                    // Get welcome video
                    const welcomeVideoUrl = await heygenManager.getWelcomeVideo();
                    
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
                    
                    // Update step image
                    updateStepImage(data.origami_type, data.step_number);
                    
                    // Update progress bar
                    const progress = (data.step_number / data.total_steps) * 100;
                    $('.progress-bar').css('width', progress + '%');
                    $('.progress-bar').attr('aria-valuenow', progress);
                    $('.progress-bar').text(`Step ${data.step_number}/${data.total_steps}`);
                    
                    // Try to use HeyGen if available
                    let usingHeyGen = false;
                    
                    if (typeof heygenManager !== 'undefined' && await heygenManager.initialize()) {
                        try {
                            // Show loading indicator
                            $('.speaking-indicator').removeClass('d-none').text('Generating avatar...');
                            
                            // Get video for this step
                            const videoUrl = await heygenManager.getStepVideo(stepNumber);
                            
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
                                        console.error('Error playing HeyGen video:', e);
                                        
                                        // Fallback to regular speech
                                        speakText(data.explanation);
                                    });
                                    
                                    // Mark as using HeyGen
                                    usingHeyGen = true;
                                    
                                    // Show the speaking indicator
                                    $('.speaking-indicator').text('Speaking...').removeClass('d-none');
                                }
                            }
                        } catch (error) {
                            console.error('Error using HeyGen for step explanation:', error);
                        }
                    }
                    
                    // If not using HeyGen, use regular speech synthesis
                    if (!usingHeyGen) {
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
                        $('#next-step').html('Finish<i class="fas fa-check ms-2"></i>');
                    } else {
                        $('#next-step').html('Next Step<i class="fas fa-arrow-right ms-2"></i>');
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
                    
                    // Try to use HeyGen if available
                    let usingHeyGen = false;
                    
                    if (typeof heygenManager !== 'undefined' && await heygenManager.initialize()) {
                        try {
                            // Show loading indicator
                            $('.speaking-indicator').removeClass('d-none').text('Generating help...');
                            
                            // Get current step
                            const currentStepText = $('#step-instruction').text();
                            
                            // Get help video
                            const videoUrl = await heygenManager.getHelpVideo(currentStepText);
                            
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
                                        console.error('Error playing HeyGen video:', e);
                                        
                                        // Fallback to regular speech
                                        speakText(data.troubleshooting);
                                    });
                                    
                                    // Mark as using HeyGen
                                    usingHeyGen = true;
                                    
                                    // Show the speaking indicator
                                    $('.speaking-indicator').text('Speaking...').removeClass('d-none');
                                }
                            }
                        } catch (error) {
                            console.error('Error using HeyGen for troubleshooting:', error);
                        }
                    }
                    
                    // If not using HeyGen, use regular speech synthesis
                    if (!usingHeyGen) {
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
            
            // Animate avatar to show listening state
            try {
                const videoElement = document.getElementById('avatar-video');
                const listeningVideoUrl = '/static/video/avatar-listening.mp4';
                
                if (videoElement) {
                    $('#avatar-video-source').attr('src', listeningVideoUrl);
                    videoElement.load();
                    videoElement.play().catch(e => console.log('Video play error:', e));
                }
            } catch (e) {
                console.error('Avatar video error:', e);
                // Fallback to old animation method
                $('#avatar-img').addClass('listening');
            }
        } else {
            // Stop listening
            recognition.stop();
            isListening = false;
            $(this).removeClass('listening').html('<i class="fas fa-microphone"></i> Voice Control');
            
            // Return to idle state
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
                // Fallback
                $('#avatar-img').removeClass('listening');
            }
        }
    });
    
    // Handle avatar source selection
    $('.dropdown-item').on('click', function(e) {
        e.preventDefault();
        const source = $(this).data('source');
        
        // Update active state
        $('.dropdown-item').removeClass('active');
        $(this).addClass('active');
        
        // Update button text to show selected source
        $('#avatar-source').html(`<i class="fas fa-user-circle"></i> ${$(this).text()}`);
        
        // For actual implementation this would switch avatar sources
        console.log(`Switched to ${source} avatar`);
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
        
        // Show speaking indicator and animate avatar
        $('.speaking-indicator').removeClass('d-none');
        
        // Switch avatar video to speaking version
        try {
            const videoElement = document.getElementById('avatar-video');
            
            // For hackathon demo purposes, this would be replaced with actual avatar video URLs
            // In production, this would dynamically load different avatar videos based on step content
            
            const speakingVideoUrl = '/static/video/avatar-speaking.mp4';
            const idleVideoUrl = '/static/video/avatar-idle.mp4';
            
            // Store the current source to go back to it when done
            const currentSrc = $('#avatar-video-source').attr('src');
            
            // If we have a speaking video, use it
            if (videoElement) {
                $('#avatar-video-source').attr('src', speakingVideoUrl);
                videoElement.load();
                videoElement.play().catch(e => console.log('Video play error:', e));
            }
        } catch (e) {
            console.error('Avatar video error:', e);
            // Fallback to old animation method
            $('#avatar-img').addClass('talking');
        }
        
        // Event handlers
        utterance.onend = function() {
            $('.speaking-indicator').addClass('d-none');
            
            // Switch back to idle video
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
                // Fallback
                $('#avatar-img').removeClass('talking');
            }
            
            currentAudio = null;
        };
        
        utterance.onerror = function() {
            $('.speaking-indicator').addClass('d-none');
            // Switch back to idle video
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
                // Fallback
                $('#avatar-img').removeClass('talking');
            }
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
    
    // Function to update step image based on origami type and step number
    function updateStepImage(origamiType, stepNumber) {
        // Map preloaded_key to directory name
        const typeMap = {
            'basic_crane': 'crane',
            'easy_dragon': 'dragon',
            'jumping_frog': 'frog',
            'lotus_flower': 'lotus'
        };
        
        const imageDir = typeMap[origamiType] || 'crane'; // Default to crane if type not found
        const imagePath = `/static/img/${imageDir}/${stepNumber}.jpg`;
        
        // Check if the image exists
        $.get(imagePath)
            .done(function() {
                // Image exists, show it
                $('#step-image').attr('src', imagePath).show();
                $('#step-image-container').show();
            })
            .fail(function() {
                // Image doesn't exist, use placeholder
                const placeholderPath = `/static/img/${imageDir}/placeholder.jpg`;
                
                // Try with placeholder
                $.get(placeholderPath)
                    .done(function() {
                        $('#step-image').attr('src', placeholderPath).show();
                        $('#step-image-container').show();
                    })
                    .fail(function() {
                        // No suitable image found, hide the container
                        $('#step-image').hide();
                        $('#step-image-container').hide();
                    });
            });
    }
    
    // Handle voices loading (Chrome needs this)
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = function() {
            // Voices loaded
        };
    }
});