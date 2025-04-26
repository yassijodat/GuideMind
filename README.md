# GuideMind

GuideMind is an AI-powered interactive instruction manual for origami, featuring an avatar guide and voice narration to help users follow along with step-by-step instructions.

## Features

- ✅ Upload manual or use preloaded origami instructions
- ✅ AI parses instructions into clear, sequential steps
- ✅ Avatar explains steps with voice narration
- ✅ User-friendly navigation with "Next" and "I'm stuck" options
- ✅ Troubleshooting support when users get stuck

## Tech Stack

- **Backend**: Python with Flask
- **AI**: Claude 3 Opus API for instruction parsing and explanations
- **Frontend**: HTML, CSS, JavaScript
- **Voice**: Web Speech API for text-to-speech

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/GuideMind.git
cd GuideMind
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Anthropic API key:
```
CLAUDE_API_KEY=your_api_key_here
```

4. Run the application:
```
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. **Start**: Choose to upload your own origami instructions or use the preloaded basic crane instructions.
2. **Follow Along**: The avatar will guide you through each step with voice narration.
3. **Navigation**: Use the "Next" and "Previous" buttons to move between steps.
4. **Get Help**: If you get stuck, click "I'm Stuck" for troubleshooting assistance.

## Project Structure

```
GuideMind/
├── app.py              # Flask web application
├── main.py             # Core GuideMind class
├── static/
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── main.js     # Frontend logic
└── templates/
    └── index.html      # Main page template
```

## Future Enhancements

- Add more preloaded origami instruction sets
- Implement user accounts to save progress
- Add image recognition to check user's progress
- Create mobile app version
- Support multiple languages
- Add 3D visualization of folding steps

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Anthropic's Claude API for powering the AI explanations
- The origami community for inspiration