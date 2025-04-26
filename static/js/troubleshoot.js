/**
 * Image-based troubleshooting module for GuideMind
 */
$(document).ready(function() {
    // Initialize image preview functionality
    $('#progress-image').on('change', function(event) {
        const imagePreview = document.getElementById('image-preview');
        const file = event.target.files[0];
        
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        } else {
            imagePreview.style.display = 'none';
        }
    });
    
    // Handle image troubleshoot form submission
    $('#image-troubleshoot-form').on('submit', function(e) {
        e.preventDefault();
        
        const description = $('#stuck-description').val();
        const imageFile = $('#progress-image')[0].files[0];
        
        if (!imageFile) {
            alert('Please upload an image of your current progress');
            return;
        }
        
        // Show loading indicator
        $('#image-analysis-loading').show();
        $('#image-analysis-result').hide();
        
        // Create form data
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('description', description);
        
        // Send to server
        $.ajax({
            url: '/api/troubleshoot/image',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                // Hide loading indicator
                $('#image-analysis-loading').hide();
                
                if (!data.success) {
                    alert(data.error || 'Error analyzing your image');
                    return;
                }
                
                // Display advice
                $('#image-analysis-result').show();
                $('#image-advice-content').html(data.advice);
                
                // If text-to-speech is available, read the advice
                if (typeof speakText === 'function') {
                    speakText(data.advice);
                }
                
                // If HeyGen avatar is available, use it to present the advice
                if (typeof heygenManager !== 'undefined' && heygenManager.isInitialized()) {
                    try {
                        // Show speaking indicator
                        $('.speaking-indicator').removeClass('d-none').text('Speaking...');
                        
                        // Generate and play a dynamic video for the help content
                        heygenManager.generateCustomVideo(data.advice)
                            .then(videoUrl => {
                                if (videoUrl) {
                                    const videoElement = document.getElementById('avatar-video');
                                    if (videoElement) {
                                        videoElement.onended = function() {
                                            $('.speaking-indicator').addClass('d-none');
                                        };
                                        
                                        videoElement.src = videoUrl;
                                        videoElement.load();
                                        videoElement.play().catch(e => {
                                            console.error('Error playing HeyGen video:', e);
                                            // Fallback to regular speech
                                            if (typeof speakText === 'function') {
                                                speakText(data.advice);
                                            }
                                        });
                                    }
                                }
                            })
                            .catch(error => {
                                console.error('HeyGen error:', error);
                                // Fallback to regular speech
                                if (typeof speakText === 'function') {
                                    speakText(data.advice);
                                }
                            });
                    } catch (error) {
                        console.error('Error using HeyGen for image troubleshooting:', error);
                    }
                }
            },
            error: function(xhr) {
                $('#image-analysis-loading').hide();
                let errorMessage = 'Failed to analyze your image';
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error) {
                        errorMessage = response.error;
                    }
                } catch (e) {
                    // Parse error, use default message
                }
                alert('Error: ' + errorMessage);
            }
        });
    });
    
    // Enhance the help button to load the troubleshooting template
    const originalHelpButtonHandler = $('#help-button').click;
    $('#help-button').off('click').on('click', function() {
        // First, load the troubleshooting panel if it doesn't exist
        if ($('#troubleshooting-container').length === 0) {
            $.ajax({
                url: '/templates/troubleshoot.html',
                type: 'GET',
                dataType: 'html',
                success: function(html) {
                    // If the template is just the container itself
                    if ($('#guide-container').length > 0) {
                        $('#guide-container').append(html);
                    } else {
                        // Fallback if the guide container isn't found
                        $('body').append(html);
                    }
                    
                    // Initialize the panel's controls
                    initTroubleshootPanel();
                    
                    // Now trigger the original handler to load the content
                    if (typeof originalHelpButtonHandler === 'function') {
                        originalHelpButtonHandler.call(this);
                    } else {
                        // Default behavior - show the panel and load troubleshooting
                        loadTroubleshooting();
                    }
                },
                error: function() {
                    console.error('Failed to load troubleshooting template');
                    // Fall back to original behavior
                    if (typeof originalHelpButtonHandler === 'function') {
                        originalHelpButtonHandler.call(this);
                    } else {
                        loadTroubleshooting();
                    }
                }
            });
        } else {
            // Panel already exists, just show it and load content
            $('#troubleshooting-container').show();
            if (typeof originalHelpButtonHandler === 'function') {
                originalHelpButtonHandler.call(this);
            } else {
                loadTroubleshooting();
            }
        }
    });
    
    // Function to initialize the panel controls
    function initTroubleshootPanel() {
        // Reset the form
        $('#image-troubleshoot-form')[0].reset();
        $('#image-preview').hide();
        $('#image-analysis-result').hide();
        
        // Add close button handler
        $('#close-troubleshooting').on('click', function() {
            $('#troubleshooting-container').hide();
            // Stop any speech that might be happening
            if (window.speechSynthesis && window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            }
        });
    }
    
    // Function to load troubleshooting content
    function loadTroubleshooting() {
        $.ajax({
            url: '/api/troubleshoot',
            type: 'GET',
            success: function(data) {
                if (data.success) {
                    $('#troubleshooting-content').html(data.troubleshooting);
                    $('#troubleshooting-container').show();
                    
                    // Speak the troubleshooting advice if text-to-speech is available
                    if (typeof speakText === 'function') {
                        speakText(data.troubleshooting);
                    }
                } else {
                    alert('Error: ' + (data.error || 'Failed to load troubleshooting'));
                }
            },
            error: function() {
                alert('Error getting troubleshooting advice. Please try again.');
            }
        });
    }
});