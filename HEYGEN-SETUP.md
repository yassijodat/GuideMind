# Setting up HeyGen for GuideMind

This guide explains how to set up and use HeyGen's video avatars with GuideMind.

## What is HeyGen?

[HeyGen](https://www.heygen.com/) is an AI-powered video generation platform that allows you to create realistic talking head videos with AI avatars. GuideMind integrates with HeyGen to provide a more engaging and interactive origami instruction experience.

## Getting a HeyGen API Key

1. Sign up for a HeyGen account at [https://www.heygen.com/](https://www.heygen.com/)
2. After creating your account, go to the API section in your account settings
3. Generate a new API key
4. Copy this key to use in your GuideMind setup

## Setting up HeyGen with GuideMind

1. Create a `.env` file in the root directory of your GuideMind project
2. Add your HeyGen API key to the `.env` file:
   ```
   HEYGEN_API_KEY=your_heygen_api_key_here
   ```
3. If you're also using Claude API, add that key as well:
   ```
   CLAUDE_API_KEY=your_claude_api_key_here
   ```

## Using HeyGen in GuideMind

Once set up, GuideMind will automatically use HeyGen to generate video avatars for:

1. The welcome message when instructions are loaded
2. Step-by-step explanations of origami instructions
3. Troubleshooting advice when you click "I'm Stuck"

### Avatar Selection

You can select from different HeyGen avatars:

1. Click the "Avatar Settings" button below the avatar video
2. In the settings modal, you can:
   - Choose from available avatars (these are the avatars in your HeyGen account)
   - Select different voices for your avatar
   - Test the selected voice

## Troubleshooting

If HeyGen integration is not working:

1. Verify your API key is correct in the `.env` file
2. Check that you have avatars available in your HeyGen account
3. Ensure you have sufficient credits in your HeyGen account
4. Check the browser console for any errors related to HeyGen integration

## HeyGen API Usage

The integration uses the following HeyGen API endpoints:

- `GET /avatar.list` - To list available avatars
- `GET /voice.list` - To list available voices
- `POST /video.generate` - To generate videos
- `GET /video.status` - To check video generation status

Each video generation consumes credits from your HeyGen account. The number of credits used depends on the length of the video.

## Fallback Mechanism

If HeyGen is not available or encounters an error, GuideMind will automatically fall back to using the browser's built-in speech synthesis for instruction narration.

## Caching

To reduce API usage and improve performance, GuideMind caches generated videos. This means videos for steps you've already viewed won't need to be regenerated when you revisit them.