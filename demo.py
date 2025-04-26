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
        self.current_origami_type = "basic_crane"  # Default type
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
            """,
            "easy_dragon": """
                1. Start with a square piece of paper, colored side up.
                2. Fold in half diagonally to make a triangle.
                3. Fold the right corner to the top point.
                4. Fold the left corner to the top point.
                5. Fold the top layer of the right and left points inward to form the dragon's head.
                6. Fold the bottom point up about 2/3 of the way.
                7. Fold this point back down, but only halfway, creating the dragon's tail.
                8. Turn the model over.
                9. Fold the top points outward at an angle to create wings.
                10. Gently pull the wings apart and adjust the head and tail to complete your dragon.
            """,
            "jumping_frog": """
                1. Start with a square piece of paper, colored side up.
                2. Fold the paper in half, then unfold.
                3. Fold the paper in half in the other direction, then unfold.
                4. Flip the paper over.
                5. Fold each corner into the center point.
                6. Fold the bottom edge up to meet the center point, then unfold.
                7. Fold the top edge down to meet the center point, then unfold.
                8. Fold the bottom corners along the crease lines to the center.
                9. Fold the top corners along the crease lines to the center.
                10. Fold in half, then fold the legs up at an angle.
                11. Press the back to make your frog jump!
            """,
            "lotus_flower": """
                1. Start with a square piece of paper, white side up.
                2. Fold diagonally in both directions and unfold.
                3. Fold all four corners to the center.
                4. Fold all four corners to the center again.
                5. Flip the paper over.
                6. Fold all four corners to the center once more.
                7. Gently start pulling out each of the flaps from underneath.
                8. Continue pulling out all eight flaps.
                9. Curve each petal gently downward to shape the flower.
                10. Adjust all petals evenly to complete your lotus flower.
            """
        }
        
        # Pre-defined explanations for demo
        self.explanations = {
            # Basic Crane
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
                "Hold the bottom point (which will become the crane's tail) and the top point (which will become the head). Gently pull them apart while pressing down on the middle section. As you do this, the wings will naturally rise up on the sides. Shape the head by folding the very tip down, and adjust the wings to the desired angle.",
            
            # Easy Dragon
            "1. Start with a square piece of paper, colored side up.":
                "Begin with a square piece of origami paper. Place it on your work surface with the colored side facing up. This ensures the colored side will show on the outside of your finished dragon.",
            
            "2. Fold in half diagonally to make a triangle.":
                "Take one corner of the square and fold it diagonally to the opposite corner to create a triangle. Make sure the edges align perfectly, then press down firmly to create a sharp crease.",
            
            "3. Fold the right corner to the top point.":
                "Take the right corner of your triangle and fold it up so that its point touches the top point of the triangle. This will create a smaller triangle on the right side.",
            
            "4. Fold the left corner to the top point.":
                "Similarly, take the left corner of your original triangle and fold it up so its point touches the top point. Now both corners are folded up, creating a rhombus or diamond shape.",
            
            "5. Fold the top layer of the right and left points inward to form the dragon's head.":
                "Focus on the top layer only. Take the right and left points that you just folded up, and fold them inward toward the center to create the dragon's head. Each should be folded approximately 1/3 of the way toward the center.",
            
            "6. Fold the bottom point up about 2/3 of the way.":
                "Take the bottom point of your model and fold it upward about 2/3 of the distance to the top. This will form the basis for the dragon's tail.",
            
            "7. Fold this point back down, but only halfway, creating the dragon's tail.":
                "Take the point you just folded up and fold it back down, but only halfway. This creates a more defined tail shape for your dragon.",
            
            "8. Turn the model over.":
                "Carefully flip the entire model over, keeping all of your creases intact. You should see the basic shape of your dragon starting to form.",
            
            "9. Fold the top points outward at an angle to create wings.":
                "Find the top points on this side (which will become the wings) and fold them outward at approximately a 45-degree angle from the body. This creates the dragon's wings.",
            
            "10. Gently pull the wings apart and adjust the head and tail to complete your dragon.":
                "Carefully open and adjust the wings to your preferred angle. Fine-tune the head shape by pressing down on the tip to create a pointed snout, and adjust the tail to curve slightly for a more natural look. Your origami dragon is complete!",
            
            # Jumping Frog
            "1. Start with a square piece of paper, colored side up.":
                "Begin with a square sheet of origami paper, placing it on your work surface with the colored side facing up. This ensures your frog will have color on the outside.",
            
            "2. Fold the paper in half, then unfold.":
                "Fold the paper in half horizontally (left edge to right edge), crease well, then unfold. This creates a center line that will guide your subsequent folds.",
            
            "3. Fold the paper in half in the other direction, then unfold.":
                "Now fold the paper in half vertically (top edge to bottom edge), crease firmly, then unfold. Your paper should now have two crease lines dividing it into quarters.",
            
            "4. Flip the paper over.":
                "Turn the paper over completely. The colored side should now be facing down.",
            
            "5. Fold each corner into the center point.":
                "Take each of the four corners and fold them into the center point where the crease lines intersect. You should end up with a square shape that's slightly smaller than your original paper.",
            
            "6. Fold the bottom edge up to meet the center point, then unfold.":
                "Take the bottom edge of your square and fold it up so that the edge meets the center point. Crease well, then unfold. This creates a reference line for later steps.",
            
            "7. Fold the top edge down to meet the center point, then unfold.":
                "Similarly, take the top edge and fold it down to the center point, crease well, and unfold. This creates another reference line.",
            
            "8. Fold the bottom corners along the crease lines to the center.":
                "Using the crease lines you just made, fold the bottom corners inward to the center. These will become the frog's back legs.",
            
            "9. Fold the top corners along the crease lines to the center.":
                "Similarly, fold the top corners inward to the center using the existing crease lines. These will form the frog's front legs.",
            
            "10. Fold in half, then fold the legs up at an angle.":
                "Fold the entire model in half toward you along the horizontal center line. Then fold the legs (the pointed corners) upward at an angle to create the jumping mechanism.",
            
            "11. Press the back to make your frog jump!":
                "Gently press down on the back of your frog to compress it, then quickly release. If done correctly, your frog should jump forward! Adjust the angle of the legs if needed to improve the jumping action.",
            
            # Lotus Flower
            "1. Start with a square piece of paper, white side up.":
                "Begin with a square piece of origami paper, placing it on your work surface with the white side (or less colorful side) facing up. The colored side will be revealed in the final petals.",
            
            "2. Fold diagonally in both directions and unfold.":
                "Fold the paper diagonally from corner to corner in both directions, making sure to crease firmly, then unfold each time. You should have an X-shaped crease pattern on your paper.",
            
            "3. Fold all four corners to the center.":
                "Take each of the four corners and fold them in to meet at the center point (where the diagonal creases intersect). You should now have a smaller square.",
            
            "4. Fold all four corners to the center again.":
                "Take the four new corners of your smaller square and fold them in to meet at the center point again. Your square is now even smaller with multiple layers.",
            
            "5. Flip the paper over.":
                "Carefully turn the entire model over, keeping all creases intact. The side with the points facing inward should now be facing down.",
            
            "6. Fold all four corners to the center once more.":
                "On this new side, fold all four corners in to meet at the center point. Your paper now has multiple layers and the beginnings of the petals are hidden within.",
            
            "7. Gently start pulling out each of the flaps from underneath.":
                "Find the flaps that are tucked under each corner (there are two per corner, for a total of eight). Carefully begin to pull them outward and upward to form the first layer of petals.",
            
            "8. Continue pulling out all eight flaps.":
                "Work your way around the model, pulling out all eight flaps carefully so they stand up to form the petals. Be gentle to avoid tearing the paper, especially at the base of each petal.",
            
            "9. Curve each petal gently downward to shape the flower.":
                "Using your fingers, gently curve each petal downward to give them a more natural, flower-like appearance. This adds dimension to your lotus flower.",
            
            "10. Adjust all petals evenly to complete your lotus flower.":
                "Make final adjustments to ensure all petals are evenly spaced and have a similar curve. Your beautiful origami lotus flower is now complete and ready to display!"
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
        self.current_origami_type = preloaded_key if preloaded_key else "custom"
        
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
            'explanation': explanation,
            'origami_type': guide.current_origami_type
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