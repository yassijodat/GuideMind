$(document).ready(function() {
    // State variables
    let totalSteps = 0;
    let currentStep = 0;
    let currentAudio = null;
    let lastExplanation = '';

    // Initialize speech synthesis
    const synth = window.speechSynthesis;
    
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
    function handleInstructionsLoaded(data) {
        if (data.success) {
            totalSteps = data.total_steps;
            currentStep = 0;
            
            // Show guide interface
            $('#setup-container').hide();
            $('#guide-container').show();
            
            // Load first step
            loadStep(0);
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
            success: function(data) {
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
                    
                    // Auto-speak the explanation
                    speakText(data.explanation);
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
            success: function(data) {
                if (data.success) {
                    $('#troubleshooting-content').html(data.troubleshooting);
                    $('#troubleshooting-container').show();
                    
                    // Speak troubleshooting advice
                    speakText(data.troubleshooting);
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
        $('.speaking-indicator').removeClass('d-none');
        
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