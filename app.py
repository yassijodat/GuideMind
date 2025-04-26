from flask import Flask, render_template, request, jsonify
import os
from main import GuideMind

app = Flask(__name__)
guide = GuideMind()

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