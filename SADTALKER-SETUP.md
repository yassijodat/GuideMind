# Setting up SadTalker for GuideMind

This guide explains how to set up and use SadTalker for creating talking face avatars in GuideMind.

## What is SadTalker?

[SadTalker](https://github.com/OpenTalker/SadTalker) is an open-source tool that can generate a talking face video from a single image and audio. GuideMind integrates with SadTalker to provide more engaging and interactive origami instruction videos.

## Setup Options

There are two ways to use SadTalker with GuideMind:

1. **Remote API** (Recommended for hackathon): Use a hosted SadTalker API service
2. **Local Installation**: Run SadTalker on your own machine

### Option 1: Remote API Setup

1. Create a `.env` file in the root directory of your GuideMind project
2. Add your SadTalker API credentials to the `.env` file:
   ```
   SADTALKER_API_URL=https://your-sadtalker-api-url.com/generate
   SADTALKER_API_KEY=your_api_key_here
   SADTALKER_USE_REMOTE=true
   ```

### Option 2: Local Installation

1. Install SadTalker by following the instructions on the [official repository](https://github.com/OpenTalker/SadTalker)
2. Once installed, create a `.env` file in the root directory of your GuideMind project
3. Add the path to your SadTalker installation:
   ```
   SADTALKER_PATH=/path/to/your/SadTalker
   SADTALKER_USE_REMOTE=false
   ```
4. Uncomment and install the required dependencies in requirements.txt:
   ```
   # For SadTalker (if used locally)
   torch>=1.10.0
   torchvision>=0.11.0
   numpy>=1.20.0
   opencv-python>=4.5.0
   face-alignment>=1.3.5
   imageio>=2.9.0
   moviepy>=1.0.3
   gfpgan>=1.3.8
   ```

## Using SadTalker in GuideMind

Once set up, GuideMind will automatically use SadTalker to generate video avatars for:

1. The welcome message when instructions are loaded
2. Step-by-step explanations of origami instructions
3. Troubleshooting advice when you click "I'm Stuck"

### Avatar Selection

You can select from different avatars or upload your own:

1. Click the "Avatar Settings" button below the avatar video
2. In the settings modal, you can:
   - Choose from available avatars
   - Upload your own image to use as an avatar

## Adding Custom Avatars

To add custom avatars:

1. Click the "Avatar Settings" button
2. Go to the "Upload Custom" tab
3. Upload a clear photo of a face (frontal view is preferred)
4. Give your avatar a name
5. Click "Upload Avatar"

The best images for SadTalker are:
- Clear, high-resolution photos
- Frontal face views with neutral expressions
- Good lighting without harsh shadows
- Simple backgrounds

## Troubleshooting

If SadTalker integration is not working:

1. **API Errors**: Verify your API credentials in the `.env` file
2. **Local Installation Issues**: Check that SadTalker is properly installed and the path is correct
3. **Video Generation Errors**: Try using a different avatar image
4. **Performance Issues**: Local SadTalker can be resource-intensive; consider reducing the resolution or using the remote API

## Fallback Mechanism

If SadTalker is not available or encounters an error, GuideMind will automatically fall back to using the browser's built-in speech synthesis for instruction narration.

## Video Caching

To reduce generation time and improve performance, GuideMind caches generated videos. This means videos for steps you've already viewed won't need to be regenerated when you revisit them.

## API Implementation Details

If you're implementing your own SadTalker API server, it should accept:
- A base64-encoded image
- A base64-encoded audio file or text to be spoken
- Parameters for face enhancement and animation style

And return:
- A base64-encoded video file
- Status information

---

For more information about SadTalker, visit the [official GitHub repository](https://github.com/OpenTalker/SadTalker).