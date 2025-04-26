# GuideMind Running Instructions

## Quick Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key**:
   Create a `.env` file in the project root directory with:
   ```
   CLAUDE_API_KEY=your_anthropic_api_key_here
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Usage Tips

- Use the preloaded origami crane instructions to test without uploading instructions
- The voice narration uses your browser's text-to-speech capability
- Click "I'm Stuck" at any step to get troubleshooting help
- Navigate between steps using the Previous/Next buttons

## Development

To run in development mode with auto-reload:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Linting and Type Checking

```bash
# Install linting tools
pip install flake8 mypy

# Run linting
flake8 *.py

# Run type checking
mypy *.py
```