import anthropic
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Anthropic client
client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
)

# Logging helper
def log(role, message):
    print(f"\n[{role.upper()}] {message}\n{'-'*40}")

# Agent 1: Planner
def planner_agent(goal):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=500,
        temperature=0,
        messages=[
            {"role": "user", "content": f"You are a planning expert. Break down this goal into 3-5 clear steps.\n\nGoal: {goal}"}
        ]
    )
    plan = response.content[0].text
    log("planner", plan)
    return plan

# Agent 2: Executor
def executor_agent(step):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=300,
        temperature=0,
        messages=[
            {"role": "user", "content": f"You are a detailed execution expert. Explain exactly how to perform this step:\n\nStep: {step}"}
        ]
    )
    execution = response.content[0].text
    log("executor", execution)
    return execution

# Orchestration: Manage context
def orchestrate(goal):
    plan = planner_agent(goal)
    steps = [line for line in plan.split("\n") if line.strip()]
    
    for idx, step in enumerate(steps, 1):
        log("system", f"Executing Step {idx}: {step}")
        executor_agent(step)
        time.sleep(1)  # Simulate "thinking time" for fun

if __name__ == "__main__":
    GOAL = "Make a ham and cheese sandwich."
    orchestrate(GOAL)
