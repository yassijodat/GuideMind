# Image-Based Troubleshooting in GuideMind

This document explains how the image upload feature works in GuideMind, allowing users to get AI-powered help when they're stuck on a specific origami step.

## Overview

The image-based troubleshooting feature enables users to:

1. Take a photo of their current origami progress
2. Upload it through the "I'm Stuck" interface
3. Describe what they're struggling with
4. Receive personalized AI guidance based on the visual analysis of their work

## Technical Implementation

### Components

1. **Frontend**:
   - HTML form for image upload in `templates/troubleshoot.html`
   - JavaScript handling in `static/js/troubleshoot.js`
   - Image preview functionality
   - Loading indicators and results display

2. **Backend**:
   - Flask route in `routes/troubleshoot.py`
   - Image processing and temporary storage
   - Claude 3 Opus API integration for image analysis
   - Secure handling of user-submitted content

3. **Integration with Claude 3 Opus**:
   - Multimodal capabilities (image + text)
   - Context-aware analysis based on current step
   - Expert troubleshooting advice

### Data Flow

1. User clicks "I'm Stuck" button
2. Troubleshooting panel appears with basic text advice
3. User takes/uploads a photo and describes their issue
4. Image is sent to server via AJAX POST request
5. Server processes and temporarily stores the image
6. Image is encoded in base64 format and sent to Claude 3 Opus
7. Claude analyzes the image and current origami step context
8. AI-generated troubleshooting advice is returned to user
9. Advice is displayed and can be read aloud through text-to-speech
10. Temporary image file is deleted from server

## Security Considerations

- Images are stored temporarily and deleted after processing
- Unique filenames prevent conflicts
- File type validation prevents uploading malicious files
- Size limits prevent DoS attacks
- No user data is permanently stored

## Avatar Integration

The feature integrates with the existing avatar system:

- If HeyGen integration is available, the avatar can verbally explain the troubleshooting advice
- Otherwise, the web browser's built-in text-to-speech reads the advice
- The avatar's facial expressions and movements enhance the experience

## Usage Example

A typical usage scenario:

1. User reaches step 3 of the origami crane instruction: "Fold the top corners to the center line"
2. User attempts the fold but isn't happy with the result
3. User clicks "I'm Stuck" button
4. User uploads a photo of their current progress
5. User types: "My corners don't line up properly"
6. Claude analyzes the image and notices uneven fold lines
7. Claude provides specific advice: "Your right corner is folded at a slight angle. Try realigning by..."

## Future Enhancements

Planned improvements for this feature:

1. Real-time camera feed analysis
2. Step-by-step visual comparison with correct examples
3. Progress tracking across sessions
4. Interactive drawing on images to highlight problem areas
5. AR overlay to demonstrate correct folding technique
6. Batch upload for complex troubleshooting scenarios

## Troubleshooting the Troubleshooter

If the image upload feature isn't working correctly:

1. Ensure the browser has camera/file access permissions
2. Check that the image is in a supported format (jpg, png, gif)
3. Verify the API key for Claude is correctly configured
4. Check server logs for any errors during image processing
5. Ensure the troubleshoot.js file is properly loaded