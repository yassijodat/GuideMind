# Image-Based Troubleshooting with Claude

This vignette demonstrates how to implement image upload functionality to help users troubleshoot where they're stuck in the origami process. 

## Overview

This example shows how to:

1. Accept image uploads from users who are stuck on a particular step
2. Send the image along with contextual information to Claude 3 Opus
3. Return AI-generated advice specific to the user's situation

## Requirements

- Anthropic API key (Claude 3 Opus model)
- Python 3.8+
- Flask web framework
- Required Python packages listed in `requirements.txt`

## Setup and Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Anthropic API key:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```
   python image_troubleshoot.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

5. Test the image upload functionality by:
   - Clicking "I'm Stuck" button
   - Describing your issue in the text area
   - Uploading a photo of your current origami progress
   - Submitting the form

## How It Works

1. The user takes a photo of their origami progress where they're stuck
2. The image is uploaded to the server via a form submission
3. The server encodes the image in base64 format
4. The image is sent to Claude 3 Opus along with context about the current step
5. Claude analyzes the image and provides specific troubleshooting advice
6. The advice is displayed to the user

## Integration with Main Application

To integrate this functionality into the main GuideMind application:

1. Add the image upload field to the troubleshooting section
2. Modify the existing troubleshooting route to handle image uploads
3. Update the front-end JavaScript to handle the image preview and submission
4. Ensure the upload directory exists and has proper permissions