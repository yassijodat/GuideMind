import anthropic
import os
from dotenv import load_dotenv

load_dotenv()  # 👈 Load the .env before anything else


# Set your Anthropic API key
client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")  # Or hardcode temporarily
)

# Define the sandwich goal
goal = "Make a simple ham and cheese sandwich."

# ---- Step 1: Ask CLAUDE 1 (Planner) ----

def ask_planner(goal):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=500,
        temperature=0,
        messages=[
            {"role": "user", "content": f"You are a planning expert. Break down this goal into 3-5 simple, clear steps.\n\nGoal: {goal}"}
        ]
    )
    steps = response.content[0].text
    return steps

# ---- Step 2: Ask CLAUDE 2 (Executor) ----

def ask_executor(step):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=300,
        temperature=0,
        messages=[
            {"role": "user", "content": f"You are a code execution expert. Explain exactly how to perform this step:\n\nStep: {step}"}
        ]
    )
    execution = response.content[0].text
    return execution

# ---- Main Orchestration ----

if __name__ == "__main__":
    # Multi-Claude orchestration
    plan = ask_planner(goal)
    print("\n🧠 PLAN (from Planner):\n")
    print(plan)

    print("\n🤖 EXECUTION (from Executor):\n")
    for idx, step in enumerate(plan.split('\n'), start=1):
        if step.strip():
            execution = ask_executor(step)
            print(f"Step {idx}: {execution}\n")
