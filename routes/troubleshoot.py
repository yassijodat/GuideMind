import os
import base64
from flask import Blueprint, request, jsonify, current_app
import anthropic

# Create Blueprint
troubleshoot_bp = Blueprint('troubleshoot', __name__)

# Initialize Anthropic client
def get_anthropic_client():
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        current_app.logger.warning("CLAUDE_API_KEY not found in environment variables")
        return None
    return anthropic.Anthropic(api_key=api_key)

def encode_image(image_path):
    """Encode image to base64 for Claude"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@troubleshoot_bp.route('/api/troubleshoot', methods=['GET'])
def get_troubleshooting():
    """Get troubleshooting tips for current step"""
    from app import guide  # Import here to avoid circular import
    
    current_step = guide.get_current_step()
    if current_step:
        troubleshooting = guide.get_troubleshooting(current_step)
        return jsonify({
            'success': True,
            'troubleshooting': troubleshooting
        })
    else:
        return jsonify({'success': False, 'error': 'No current step'})

@troubleshoot_bp.route('/api/troubleshoot/image', methods=['POST'])
def image_troubleshoot():
    """Get troubleshooting tips based on uploaded image"""
    # Ensure uploads directory exists
    uploads_dir = os.path.join(current_app.static_folder, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    from app import guide  # Import here to avoid circular import
    
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    # Get image and user's description of the problem
    user_image = request.files['image']
    user_description = request.form.get('description', 'I am stuck')
    
    # Get the current step
    current_step = guide.get_current_step()
    if not current_step:
        return jsonify({'success': False, 'error': 'No current step'}), 400
    
    # Get the step explanation for additional context
    step_explanation = guide.get_step_explanation(current_step)
    
    # Validate image
    if user_image.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'}), 400
    
    if not user_image.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'success': False, 'error': 'File type not allowed'}), 400
    
    # Save image temporarily with a unique filename
    import uuid
    temp_filename = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(uploads_dir, temp_filename)
    user_image.save(image_path)
    
    try:
        # Get Anthropic client
        client = get_anthropic_client()
        if not client:
            return jsonify({'success': False, 'error': 'Claude API not configured'}), 500
        
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
                            "text": f"""I'm working on an origami project and I'm stuck at this step:
                            
Current step: {current_step}

Explanation of this step: {step_explanation}

User description of the problem: {user_description}

Please analyze the image of my current progress and:
1. Identify what might be going wrong
2. Explain exactly how to fix it
3. Provide clear, specific guidance on the correct folding technique
4. Describe what the result should look like when done correctly

Respond with specific, actionable advice that directly addresses what's visible in the image."""
                        }
                    ]
                }
            ]
        )
        
        # Extract the troubleshooting advice
        troubleshooting_advice = response.content[0].text
        
        return jsonify({
            'success': True,
            'advice': troubleshooting_advice
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in image troubleshooting: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        # Cleanup: remove temporary image
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            current_app.logger.error(f"Error removing temporary image: {str(e)}")