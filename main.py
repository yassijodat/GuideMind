import anthropic
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
)

class GuideMind:
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
    
    def parse_instructions(self, manual_text=None, preloaded_key=None):
        """Parse either uploaded manual text or use preloaded instructions"""
        if preloaded_key and preloaded_key in self.preloaded_instructions:
            instruction_text = self.preloaded_instructions[preloaded_key]
        elif manual_text:
            instruction_text = manual_text
        else:
            return False
        
        # Use Claude to parse and structure the instructions
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0,
            messages=[
                {"role": "user", "content": f"""
                Parse these origami instructions into clear, sequential steps.
                For each step:
                1. Identify the main action
                2. Describe it precisely 
                3. Format as a list of steps
                
                Instructions:
                {instruction_text}
                """}
            ]
        )
        
        parsed_steps = response.content[0].text
        self.instructions = [step.strip() for step in parsed_steps.split('\n') if step.strip()]
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
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": f"""
                You are an expert origami instructor. Explain this step in detail:
                
                Step: {step_text}
                
                Provide a clear, detailed explanation that would help a beginner understand exactly what to do.
                """}
            ]
        )
        
        return response.content[0].text
    
    def get_troubleshooting(self, step_text):
        """Get troubleshooting advice for when user is stuck"""
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": f"""
                A user is stuck on this origami step:
                
                Step: {step_text}
                
                Provide troubleshooting advice including:
                1. Common mistakes at this step
                2. How to identify if the fold is correct
                3. Remedial actions (e.g., "try refolding the top corner")
                4. A simple check to confirm they're back on track
                """}
            ]
        )
        
        return response.content[0].text

# Demo usage
if __name__ == "__main__":
    guide = GuideMind()
    guide.parse_instructions(preloaded_key="basic_crane")
    
    print("Welcome to GuideMind - Origami Assistant!")
    print("We'll guide you through making an origami crane.")
    print("-" * 50)
    
    while True:
        current_step = guide.get_current_step()
        if not current_step:
            print("You've completed all the steps! 🎉")
            break
        
        explanation = guide.get_step_explanation(current_step)
        print(f"\nStep {guide.current_step + 1}: {current_step}")
        print(f"\n{explanation}\n")
        
        action = input("Type 'next', 'back', 'help', or 'quit': ").lower()
        
        if action == 'next':
            if not guide.next_step():
                print("That was the last step!")
        elif action == 'back':
            if not guide.previous_step():
                print("You're already at the first step!")
        elif action == 'help':
            troubleshooting = guide.get_troubleshooting(current_step)
            print("\n--- TROUBLESHOOTING ---")
            print(troubleshooting)
        elif action == 'quit':
            print("Thanks for using GuideMind!")
            break
        else:
            print("Invalid command. Try again.")