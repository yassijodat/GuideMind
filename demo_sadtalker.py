from flask import Flask, render_template, request, jsonify
import os
import json
import time
import random
from sadtalker_controller import sadtalker_controller

app = Flask(__name__)

# Demo guide class with mock data
class DemoGuide:
    def __init__(self):
        self.instructions = []
        self.current_step = 0
        self.preloaded_instructions = {
            "basic_crane": [
                "Start with a square piece of paper, colored side down.",
                "Fold the paper in half diagonally to form a triangle.",
                "Fold the triangle in half to form a smaller triangle.",
                "Open the paper up to the first triangle.",
                "Fold the corners of the triangle to the center point.",
                "Turn the paper over.",
                "Fold the corners to the center again.",
                "Fold the bottom edges to the center line.",
                "Fold the paper in half backward along the center line.",
                "Pull the wings up and press the body down to form a crane."
            ]
        }
        
        # Detailed explanations for each step
        self.explanations = {
            "Start with a square piece of paper, colored side down.": 
                "Begin with a perfectly square sheet of origami paper. If you're using paper that's colored on one side, place it on your work surface with the colored side facing down (white side up). This ensures the colored side will show on the outside of your finished crane.",
            
            "Fold the paper in half diagonally to form a triangle.":
                "Take the bottom right corner of the square and fold it up to the top left corner, creating a diagonal fold that divides the square into a triangle. Make sure the edges align perfectly, then crease the fold firmly by running your finger along it.",
            
            "Fold the triangle in half to form a smaller triangle.":
                "Take the right point of your triangle and fold it over to meet the left point, creating a smaller triangle. Again, make sure the edges align perfectly before creasing the fold firmly.",
            
            "Open the paper up to the first triangle.":
                "Carefully unfold the paper back to the larger triangle shape from step 2. You should still see the crease from step 3 running from the top point to the middle of the base.",
            
            "Fold the corners of the triangle to the center point.":
                "Take both the left and right corners of the triangle and fold them inward so their points meet at the top point of the triangle. The paper will now resemble a diamond shape or a kite.",
            
            "Turn the paper over.":
                "Carefully flip the entire model over from left to right, keeping all your creases intact. The model should still look like a diamond shape.",
            
            "Fold the corners to the center again.":
                "Similar to step 5, take the left and right corners of the diamond and fold them inward so they meet at the center crease. This will create a narrower diamond shape.",
            
            "Fold the bottom edges to the center line.":
                "Take the bottom flaps on both sides and fold them upward along the center line. These will form the wings of your crane later.",
            
            "Fold the paper in half backward along the center line.":
                "Fold the entire model in half backward (away from you) along the vertical center line. The folded wings should be on the outside of this fold.",
            
            "Pull the wings up and press the body down to form a crane.":
                "Hold the bottom point (which will become the crane's tail) and the top point (which will become the head). Gently pull them apart while pressing down on the middle section. As you do this, the wings will naturally rise up on the sides. Shape the head by folding the very tip down, and adjust the wings to the desired angle."
        }
        
        # Troubleshooting advice for each step
        self.troubleshooting = {
            "Start with a square piece of paper, colored side down.": 
                "Common mistakes:\n- Using rectangular paper instead of square\n- Starting with colored side up\n\nCheck if correct:\n- Paper should be perfectly square (all sides equal)\n- White/plain side should be facing up\n\nRemediation:\n- If using printer paper, fold one corner to the opposite edge and cut off excess\n- Flip the paper if the colored side is facing up\n\nConfirmation check:\n- Place paper on flat surface and ensure all corners line up",
            
            "Fold the paper in half diagonally to form a triangle.": 
                "Common mistakes:\n- Folding horizontally or vertically instead of diagonally\n- Not aligning corners precisely\n\nCheck if correct:\n- You should have a perfect triangle\n- The fold should run from one corner to the opposite corner\n\nRemediation:\n- Unfold and try again, making sure to bring one corner directly to the opposite corner\n- Smooth out the paper and ensure it's flat before folding\n\nConfirmation check:\n- The triangle should have two equal sides",
            
            # Add more troubleshooting advice for other steps...
        }
    
    def parse_instructions(self, manual_text=None, preloaded_key=None):
        """Parse either uploaded manual text or use preloaded instructions"""
        if preloaded_key and preloaded_key in self.preloaded_instructions:
            self.instructions = self.preloaded_instructions[preloaded_key]
            self.current_step = 0
            return True
        elif manual_text:
            # For demo, just split by lines
            self.instructions = [line.strip() for line in manual_text.split('\n') if line.strip()]
            self.current_step = 0
            return True
        return False
    
    def get_current_step(self):
        """Get the current step instruction"""
        if 0 <= self.current_step < len(self.instructions):
            return self.instructions[self.current_step]
        return None
    
    def next_step(self):
        """Move to next step if available"""
        if self.current_step < len(self.instructions) - 1:
            self.current_step += 1
            return True
        return False
    
    def previous_step(self):
        """Move to previous step if available"""
        if self.current_step > 0:
            self.current_step -= 1
            return True
        return False
    
    def get_step_explanation(self, step_text):
        """Get detailed explanation for a particular step"""
        return self.explanations.get(step_text, f"Here's how to do this step: {step_text} Make sure to crease all folds firmly and keep your work neat.")
    
    def get_troubleshooting(self, step_text):
        """Get troubleshooting advice for when user is stuck"""
        return self.troubleshooting.get(step_text, f"If you're having trouble with '{step_text}', try the following:\n\n1. Check that your previous folds are accurate\n2. Make sure your paper is properly aligned\n3. Use your fingernail to make crisp, clean folds\n4. If necessary, start over with a new piece of paper")

# Create a guide instance
guide = DemoGuide()

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
    try:
        if 'manual' in request.files:
            file = request.files['manual']
            # Process uploaded file
            manual_text = file.read().decode('utf-8')
            success = guide.parse_instructions(manual_text=manual_text)
        else:
            # Use preloaded instructions
            preloaded_key = request.form.get('preloaded_key', 'basic_crane')
            print(f"Loading preloaded instructions: {preloaded_key}")
            success = guide.parse_instructions(preloaded_key=preloaded_key)
        
        if success:
            return jsonify({
                'success': True,
                'total_steps': len(guide.instructions)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to load instructions'})
    except Exception as e:
        print(f"Error loading instructions: {e}")
        return jsonify({'success': False, 'error': f'Error loading instructions: {str(e)}'})

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
    
    # For demo, pretend it's available
    return jsonify({
        'status': 'success',
        'initialized': True,
        'message': 'SadTalker initialized successfully'
    })

@app.route('/api/avatar/options', methods=['GET'])
def avatar_options():
    """Get available avatar options"""
    # Return mock avatars for demo
    mock_avatars = [
        {
            "id": "professional_male",
            "name": "Professional Male",
            "thumbnail": "/static/img/avatars/default-male.jpg"
        },
        {
            "id": "professional_female",
            "name": "Professional Female",
            "thumbnail": "/static/img/avatars/default-female.jpg"
        }
    ]
    
    return jsonify({
        'status': 'success',
        'avatars': mock_avatars
    })

@app.route('/api/avatar/set', methods=['POST'])
def set_avatar():
    """Set avatar to use"""
    data = request.json
    avatar_id = data.get('avatar_id')
    
    if not avatar_id:
        return jsonify({
            'status': 'error',
            'message': 'No avatar_id provided'
        })
    
    # For demo, always succeed
    return jsonify({
        'status': 'success',
        'message': 'Avatar set successfully'
    })

@app.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """Upload a custom avatar image"""
    if 'image' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No image file provided'
        })
    
    # For demo, just return mock data
    custom_id = f"custom_{int(time.time())}"
    name = request.form.get('name', f"Custom Avatar")
    
    return jsonify({
        'status': 'success',
        'avatar': {
            "id": custom_id,
            "name": name,
            "thumbnail": "/static/img/avatars/default-custom.jpg"
        },
        'message': 'Avatar uploaded successfully'
    })

@app.route('/api/avatar/welcome-video', methods=['GET'])
def get_welcome_video():
    """Get welcome video"""
    # For demo, just return a placeholder video
    time.sleep(1)  # Simulate processing time
    
    return jsonify({
        'status': 'success',
        'video_url': '/static/videos/welcome-placeholder.mp4',
        'cached': False
    })

@app.route('/api/avatar/step-video/<int:step_number>', methods=['GET'])
def get_step_video(step_number):
    """Get video for a specific step"""
    # For demo, just return a placeholder video
    time.sleep(1)  # Simulate processing time
    
    return jsonify({
        'status': 'success',
        'video_url': '/static/videos/step-placeholder.mp4',
        'cached': False
    })

@app.route('/api/avatar/help-video', methods=['POST'])
def get_help_video():
    """Get help video for when user is stuck"""
    # For demo, just return a placeholder video
    time.sleep(1)  # Simulate processing time
    
    return jsonify({
        'status': 'success',
        'video_url': '/static/videos/help-placeholder.mp4',
        'cached': False
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/img/avatars', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)
    
    # Create placeholder videos if they don't exist
    for video_name in ['welcome-placeholder.mp4', 'step-placeholder.mp4', 'help-placeholder.mp4']:
        video_path = os.path.join('static/videos', video_name)
        if not os.path.exists(video_path):
            # Create a blank README file instead of video for demo
            with open(video_path, 'w') as f:
                f.write(f"# Placeholder for {video_name}\n\nThis would be a real video in production.")
    
    # Create placeholder avatar images if they don't exist
    for avatar_name in ['default-male.jpg', 'default-female.jpg', 'default-custom.jpg']:
        avatar_path = os.path.join('static/img/avatars', avatar_name)
        if not os.path.exists(avatar_path):
            # Create a blank README file instead of image for demo
            with open(avatar_path, 'w') as f:
                f.write(f"# Placeholder for {avatar_name}\n\nThis would be a real image in production.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)