from flask import Flask, render_template, request, jsonify
import os
import json

# Create the Flask app
app = Flask(__name__)

# Mock GuideMind class for demonstration
class MockGuideMind:
    def __init__(self):
        self.instructions = []
        self.current_step = 0
        self.preloaded_instructions = {
            "basic_crane": """
                1. Start with a square piece of paper, colored side down.
                2. Fold the paper in half diagonally to form a triangle.
                3. Fold the triangle in half to form a smaller triangle.
                4. Open the paper up to the first triangle.
                5. Fold the corners of the triangle to the center point.
                6. Turn the paper over.
                7. Fold the corners to the center again.
                8. Fold the bottom edges to the center line.
                9. Fold the paper in half backward along the center line.
                10. Pull the wings up and press the body down to form a crane.
            """
        }
        
        # Pre-defined explanations for demo
        self.explanations = {
            "1. Start with a square piece of paper, colored side down.": 
                "Begin with a perfectly square sheet of origami paper. If you're using paper that's colored on one side, place it on your work surface with the colored side facing down (white side up). This ensures the colored side will show on the outside of your finished crane.",
            
            "2. Fold the paper in half diagonally to form a triangle.":
                "Take the bottom right corner of the square and fold it up to the top left corner, creating a diagonal fold that divides the square into a triangle. Make sure the edges align perfectly, then crease the fold firmly by running your finger along it.",
            
            "3. Fold the triangle in half to form a smaller triangle.":
                "Take the right point of your triangle and fold it over to meet the left point, creating a smaller triangle. Again, make sure the edges align perfectly before creasing the fold firmly.",
            
            "4. Open the paper up to the first triangle.":
                "Carefully unfold the paper back to the larger triangle shape from step 2. You should still see the crease from step 3 running from the top point to the middle of the base.",
            
            "5. Fold the corners of the triangle to the center point.":
                "Take both the left and right corners of the triangle and fold them inward so their points meet at the top point of the triangle. The paper will now resemble a diamond shape or a kite.",
            
            "6. Turn the paper over.":
                "Carefully flip the entire model over from left to right, keeping all your creases intact. The model should still look like a diamond shape.",
            
            "7. Fold the corners to the center again.":
                "Similar to step 5, take the left and right corners of the diamond and fold them inward so they meet at the center crease. This will create a narrower diamond shape.",
            
            "8. Fold the bottom edges to the center line.":
                "Take the bottom flaps on both sides and fold them upward along the center line. These will form the wings of your crane later.",
            
            "9. Fold the paper in half backward along the center line.":
                "Fold the entire model in half backward (away from you) along the vertical center line. The folded wings should be on the outside of this fold.",
            
            "10. Pull the wings up and press the body down to form a crane.":
                "Hold the bottom point (which will become the crane's tail) and the top point (which will become the head). Gently pull them apart while pressing down on the middle section. As you do this, the wings will naturally rise up on the sides. Shape the head by folding the very tip down, and adjust the wings to the desired angle."
        }
        
        # Pre-defined troubleshooting advice for demo
        self.troubleshooting = {
            "1. Start with a square piece of paper, colored side down.": 
                "Common mistakes:\n- Using rectangular paper instead of square\n- Starting with colored side up\n\nCheck if correct:\n- Paper should be perfectly square (all sides equal)\n- White/plain side should be facing up\n\nRemediation:\n- If using printer paper, fold one corner to the opposite edge and cut off excess\n- Flip the paper if the colored side is facing up\n\nConfirmation check:\n- Place paper on flat surface and ensure all corners line up",
            
            "2. Fold the paper in half diagonally to form a triangle.": 
                "Common mistakes:\n- Folding horizontally or vertically instead of diagonally\n- Not aligning corners precisely\n\nCheck if correct:\n- You should have a perfect triangle\n- The fold should run from one corner to the opposite corner\n\nRemediation:\n- Unfold and try again, making sure to bring one corner directly to the opposite corner\n- Smooth out the paper and ensure it's flat before folding\n\nConfirmation check:\n- The triangle should have two equal sides",
            
            # Additional troubleshooting entries would be added here
        }
    
    def parse_instructions(self, manual_text=None, preloaded_key=None):
        """Parse either uploaded manual text or use preloaded instructions"""
        if preloaded_key and preloaded_key in self.preloaded_instructions:
            instruction_text = self.preloaded_instructions[preloaded_key]
        elif manual_text:
            instruction_text = manual_text
        else:
            return False
        
        # For the mock, we'll just split by lines
        self.instructions = [step.strip() for step in instruction_text.split('\n') if step.strip()]
        self.current_step = 0
        return True
    
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
        return self.explanations.get(step_text, f"Explanation for: {step_text}")
    
    def get_troubleshooting(self, step_text):
        """Get troubleshooting advice for when user is stuck"""
        return self.troubleshooting.get(step_text, f"Troubleshooting advice for: {step_text}")


# Create a mock guide instance
guide = MockGuideMind()

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

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)