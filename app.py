from flask import Flask, render_template, request, jsonify
import os
import json
from main import GuideMind
from sadtalker_controller import sadtalker_controller

app = Flask(__name__)
guide = GuideMind()

# Initialize SadTalker controller
try:
    sadtalker_initialized = sadtalker_controller.is_available()
    print(f"SadTalker initialized: {sadtalker_initialized}")
    
    # Add sample avatars if needed
    if sadtalker_initialized and not sadtalker_controller.available_avatars:
        added_avatars = sadtalker_controller.add_sample_avatars()
        print(f"Added {len(added_avatars)} sample avatars")
except Exception as e:
    print(f"Error initializing SadTalker: {e}")
    sadtalker_initialized = False

@app.route('/')
def index():
    # Main interface page
    return render_template('index.html')

@app.route('/load-instructions', methods=['POST'])
def load_instructions():
    if 'manual' in request.files:
        file = request.files['manual']
        # Process uploaded file
        manual_text = file.read().decode('utf-8')
        success = guide.parse_instructions(manual_text=manual_text)
    else:
        # Use preloaded instructions
        preloaded_key = request.form.get('preloaded_key', 'basic_crane')
        success = guide.parse_instructions(preloaded_key=preloaded_key)
    
    if success:
        return jsonify({
            'success': True,
            'total_steps': len(guide.instructions)
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to load instructions'})

@app.route('/get-step', methods=['GET'])
def get_step():
    step_number = int(request.args.get('step', guide.current_step))
    
    # Ensure valid step number
    if 0 <= step_number < len(guide.instructions):
        guide.current_step = step_number
        current_step = guide.get_current_step()
        explanation = guide.get_step_explanation(current_step)
        
        return jsonify({
            'success': True,
            'step_number': step_number + 1,
            'total_steps': len(guide.instructions),
            'instruction': current_step,
            'explanation': explanation
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid step number'})

@app.route('/troubleshoot', methods=['GET'])
def troubleshoot():
    current_step = guide.get_current_step()
    if current_step:
        troubleshooting = guide.get_troubleshooting(current_step)
        return jsonify({
            'success': True,
            'troubleshooting': troubleshooting
        })
    else:
        return jsonify({'success': False, 'error': 'No current step'})

@app.route('/next-step', methods=['POST'])
def next_step():
    if guide.next_step():
        return get_step()
    else:
        return jsonify({
            'success': False,
            'error': 'Already at last step',
            'is_complete': True
        })

@app.route('/previous-step', methods=['POST'])
def previous_step():
    if guide.previous_step():
        return get_step()
    else:
        return jsonify({
            'success': False,
            'error': 'Already at first step'
        })

# SadTalker API Routes

@app.route('/api/avatar/status', methods=['GET'])
def avatar_status():
    """Check if SadTalker is available and initialized"""
    global sadtalker_initialized
    
    if not sadtalker_initialized:
        try:
            sadtalker_initialized = sadtalker_controller.is_available()
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error initializing SadTalker: {str(e)}',
                'initialized': False
            })
    
    return jsonify({
        'status': 'success',
        'initialized': sadtalker_initialized,
        'message': 'SadTalker initialized successfully' if sadtalker_initialized else 'SadTalker not initialized'
    })

@app.route('/api/avatar/options', methods=['GET'])
def avatar_options():
    """Get available avatar options"""
    try:
        avatars = sadtalker_controller.get_avatar_options()
        return jsonify({
            'status': 'success',
            'avatars': avatars
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching avatars: {str(e)}'
        })

@app.route('/api/avatar/set', methods=['POST'])
def set_avatar():
    """Set avatar to use"""
    try:
        data = request.json
        avatar_id = data.get('avatar_id')
        
        if not avatar_id:
            return jsonify({
                'status': 'error',
                'message': 'No avatar_id provided'
            })
        
        success = sadtalker_controller.set_avatar(avatar_id)
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Avatar set successfully' if success else 'Failed to set avatar'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error setting avatar: {str(e)}'
        })

@app.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """Upload a custom avatar image"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No image file provided'
            })
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No image file selected'
            })
        
        # Get name from form data or use filename
        name = request.form.get('name', os.path.splitext(image_file.filename)[0])
        
        # Read image data
        image_data = image_file.read()
        
        # Upload avatar
        avatar = sadtalker_controller.upload_custom_avatar(image_data, name)
        
        if avatar:
            return jsonify({
                'status': 'success',
                'avatar': avatar,
                'message': 'Avatar uploaded successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to upload avatar'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error uploading avatar: {str(e)}'
        })

@app.route('/api/avatar/welcome-video', methods=['GET'])
def get_welcome_video():
    """Get welcome video"""
    force_regenerate = request.args.get('force', 'false').lower() == 'true'
    
    try:
        result = sadtalker_controller.get_welcome_video(force_regenerate=force_regenerate)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating welcome video: {str(e)}'
        })

@app.route('/api/avatar/step-video/<int:step_number>', methods=['GET'])
def get_step_video(step_number):
    """Get video for a specific step"""
    force_regenerate = request.args.get('force', 'false').lower() == 'true'
    
    try:
        current_step = guide.instructions[step_number] if 0 <= step_number < len(guide.instructions) else None
        
        if not current_step:
            return jsonify({
                'status': 'error',
                'message': f'Invalid step number: {step_number}'
            })
        
        result = sadtalker_controller.get_video_for_step(
            step_text=current_step, 
            step_number=step_number,
            force_regenerate=force_regenerate
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating step video: {str(e)}'
        })

@app.route('/api/avatar/help-video', methods=['POST'])
def get_help_video():
    """Get help video for when user is stuck"""
    force_regenerate = request.args.get('force', 'false').lower() == 'true'
    
    try:
        data = request.json
        step_text = data.get('step_text')
        
        if not step_text:
            current_step = guide.get_current_step()
            if not current_step:
                return jsonify({
                    'status': 'error',
                    'message': 'No current step'
                })
            step_text = current_step
        
        result = sadtalker_controller.get_help_video(
            step_text=step_text,
            force_regenerate=force_regenerate
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating help video: {str(e)}'
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)