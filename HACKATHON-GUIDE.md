# GuideMind Hackathon Guide

This guide will help you present GuideMind at your hackathon.

## Quick Setup (No API Keys Required)

1. Clone the repository:
   ```bash
   git clone https://github.com/yassijodat/GuideMind
   cd GuideMind
   ```

2. Install Flask (only dependency needed for the demo):
   ```bash
   pip install flask
   ```

3. Run the demo version:
   ```bash
   python demo_sadtalker.py
   ```

4. Open your browser and go to `http://localhost:5000`

## Demo Features to Showcase

### 1. Introduction Screen
- Explain the concept: "GuideMind is an AI-powered guide that walks you through origami with an avatar and voice narration"
- Point out the two options: uploading instructions or using preloaded ones
- Click "Basic Origami Crane" to start the demo

### 2. Avatar System
- Click the "Avatar Settings" button below the avatar
- Show how users can select different avatars
- Demonstrate the "Upload Custom" tab where users can add their own avatar
- Explain that in the full version, these are real talking face videos

### 3. Step-by-Step Instructions
- Show how the avatar explains each origami step
- Point out the clear step title and explanation text
- Demonstrate navigation using the "Next" and "Previous" buttons
- Show the progress bar indicating where you are in the instructions

### 4. Voice Control
- Click the "Voice Control" button
- Explain that users can navigate with voice commands like:
  - "Next" to go to the next step
  - "Back" to go to the previous step
  - "Help" when they're stuck
  - "Repeat" to hear the instructions again

### 5. Troubleshooting
- Click "I'm Stuck" to show the troubleshooting panel
- Point out the detailed help provided for that specific step
- Show the option to upload a photo of their progress for AI analysis
- Explain how this helps users overcome challenges

## Technical Highlights to Mention

1. **AI Integration**
   - Claude API for parsing instructions and generating explanations
   - SadTalker for generating talking face videos from a single image

2. **Responsive Design**
   - Works on all devices: desktop, tablet, and mobile
   - Adapts UI to different screen sizes

3. **Voice Technologies**
   - Speech synthesis for narration
   - Speech recognition for voice commands

4. **Integration Flexibility**
   - Can work with different avatar technologies (HeyGen, D-ID, SadTalker)
   - Modular design for easy extension

## Full Version Features (With API Keys)

Mention that the full version includes:
- Real AI-generated explanations using Claude
- Actual talking face videos via SadTalker API
- Real-time image analysis of user-uploaded photos
- Custom instruction parsing from any document

## Q&A Preparation

Be ready to answer these common questions:

1. **"How does it work with other types of instructions?"**
   - The AI can parse any structured instructions, not just origami
   - It works well with cooking recipes, DIY projects, assembly instructions, etc.

2. **"How customizable is the avatar?"**
   - Users can upload any face photo to create their own custom avatar
   - The system can be extended to support different voices and languages

3. **"What's the business model/use case?"**
   - Educational platforms for visual learners
   - Customer support for product assembly
   - Accessibility enhancement for instruction manuals
   - Corporate training and onboarding

4. **"What's next for GuideMind?"**
   - Mobile app version
   - Integration with AR/VR for 3D instructions
   - Support for multiple languages
   - Real-time feedback based on camera input

## Technical Demo Tips

- Have the demo already running when judges approach
- If possible, have a real origami paper and follow along with a step
- If the server crashes, just restart it - the demo is designed to be resilient
- Keep a backup copy of `demo_sadtalker.py` in case you need to make quick fixes

Good luck with your hackathon presentation!