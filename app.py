from flask import Flask, render_template, request, jsonify
import os
import json
from main import GuideMind
from heygen_controller import heygen_controller

app = Flask(__name__)
guide = GuideMind()

# Initialize HeyGen controller
try:
    heygen_initialized = heygen_controller.initialize()
    print(f"HeyGen API initialized: {heygen_initialized}")
except Exception as e:
    print(f"Error initializing HeyGen API: {e}")
    heygen_initialized = False

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

# HeyGen API Routes

@app.route('/api/heygen/status', methods=['GET'])
def heygen_status():
    """Check if HeyGen API is available and initialized"""
    global heygen_initialized
    
    if not heygen_initialized:
        try:
            heygen_initialized = heygen_controller.initialize()
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error initializing HeyGen API: {str(e)}',
                'initialized': False
            })
    
    return jsonify({
        'status': 'success',
        'initialized': heygen_initialized,
        'message': 'HeyGen API initialized successfully' if heygen_initialized else 'HeyGen API not initialized'
    })

@app.route('/api/heygen/avatars', methods=['GET'])
def heygen_avatars():
    """Get available HeyGen avatars"""
    try:
        avatars = heygen_controller.get_avatar_options()
        return jsonify({
            'status': 'success',
            'avatars': avatars
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching avatars: {str(e)}'
        })

@app.route('/api/heygen/voices', methods=['GET'])
def heygen_voices():
    """Get available HeyGen voices"""
    try:
        voices = heygen_controller.get_voice_options()
        return jsonify({
            'status': 'success',
            'voices': voices
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching voices: {str(e)}'
        })

@app.route('/api/heygen/set-avatar', methods=['POST'])
def set_heygen_avatar():
    """Set HeyGen avatar to use"""
    try:
        data = request.json
        avatar_id = data.get('avatar_id')
        
        if not avatar_id:
            return jsonify({
                'status': 'error',
                'message': 'No avatar_id provided'
            })
        
        success = heygen_controller.set_avatar(avatar_id)
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Avatar set successfully' if success else 'Failed to set avatar'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error setting avatar: {str(e)}'
        })

@app.route('/api/heygen/set-voice', methods=['POST'])
def set_heygen_voice():
    """Set HeyGen voice to use"""
    try:
        data = request.json
        voice_id = data.get('voice_id')
        
        if not voice_id:
            return jsonify({
                'status': 'error',
                'message': 'No voice_id provided'
            })
        
        success = heygen_controller.set_voice(voice_id)
        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Voice set successfully' if success else 'Failed to set voice'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error setting voice: {str(e)}'
        })

@app.route('/api/heygen/welcome-video', methods=['GET'])
def get_welcome_video():
    """Get welcome video from HeyGen"""
    force_regenerate = request.args.get('force', 'false').lower() == 'true'
    
    try:
        result = heygen_controller.get_welcome_video(force_regenerate=force_regenerate)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error generating welcome video: {str(e)}'
        })

@app.route('/api/heygen/step-video/<int:step_number>', methods=['GET'])
def get_step_video(step_number):
    """Get video for a specific step from HeyGen"""
    force_regenerate = request.args.get('force', 'false').lower() == 'true'
    
    try:
        current_step = guide.instructions[step_number] if 0 <= step_number < len(guide.instructions) else None
        
        if not current_step:
            return jsonify({
                'status': 'error',
                'message': f'Invalid step number: {step_number}'
            })
        
        result = heygen_controller.get_video_for_step(
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

@app.route('/api/heygen/help-video', methods=['POST'])
def get_help_video():
    """Get help video from HeyGen for when user is stuck"""
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
        
        result = heygen_controller.get_help_video(
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