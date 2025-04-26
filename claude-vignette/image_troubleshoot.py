import anthropic
import os
import base64
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Anthropic client
api_key = os.getenv("CLAUDE_API_KEY")
if not api_key:
    print("WARNING: CLAUDE_API_KEY not found in environment variables.")
    api_key = "dummy_key_for_testing"

client = anthropic.Anthropic(api_key=api_key)

def encode_image(image_path):
    """Encode image to base64 for Claude"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/troubleshoot', methods=['POST'])
def troubleshoot():
    if 'userImage' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Get image and user's description of the problem
    user_image = request.files['userImage']
    user_description = request.form.get('description', 'I am stuck')
    current_step = request.form.get('currentStep', 'unknown step')
    
    # Validate image
    if user_image.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not user_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Save image temporarily
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], user_image.filename)
    user_image.save(image_path)
    
    # Encode image for Claude
    base64_image = encode_image(image_path)
    
    # Prepare the Claude message with the image
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.2,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": f"I'm trying to follow origami instructions but I'm stuck at '{current_step}'. Here's a photo of my current progress. {user_description}. Can you identify what I might be doing wrong and how to fix it? Please provide clear, specific guidance."
                    }
                ]
            }
        ]
    )
    
    # Extract the troubleshooting advice
    troubleshooting_advice = response.content[0].text
    
    # Cleanup: remove temporary image
    try:
        os.remove(image_path)
    except:
        pass  # Ignore cleanup errors
    
    return jsonify({
        'advice': troubleshooting_advice
    })

if __name__ == "__main__":
    app.run(debug=True)