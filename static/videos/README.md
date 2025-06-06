# Generated Videos Directory

This directory contains videos generated by SadTalker for GuideMind.

## Video Types

The application generates several types of videos:

1. **Welcome videos**: Played when instructions are first loaded
2. **Step explanation videos**: Generated for each step in the origami instructions
3. **Help videos**: Created when the user clicks "I'm stuck"

## Video Naming

Videos follow a specific naming convention:

- `welcome.mp4`: Welcome introduction video
- `step_{number}.mp4`: Videos for each step
- `help_{timestamp}.mp4`: Troubleshooting help videos

## Caching

Videos are cached to improve performance. The application will store generated videos in this directory and reuse them when needed instead of regenerating them each time.

## Video Format

Videos are typically MP4 format with H.264 encoding at 720p resolution.

## Storage Management

The application does not automatically clean up old videos. If this directory becomes too large, you may want to manually remove older videos that are no longer needed.