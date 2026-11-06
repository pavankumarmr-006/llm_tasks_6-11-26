
import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load API keys
load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# OpenAI function
def ask_openai(prompt):
    response = openai_client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )

    print("OpenAI Answer:", response.choices[0].message.content)
    print("Model:", response.model)
    print("Token Usage:", response.usage)


# Claude function
def ask_claude(prompt, system):
    response = claude_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
        system=system
    )

    print("Claude Answer:", response.content[0].text)
    print("Model:", response.model)
    print("Token Usage:", response.usage)


# Three questions
questions = [
    "What is Artificial Intelligence?",
    "What is Python?",
    "What are Large Language Models?"
]

# Ask both AI models
for question in questions:
    print("\nQuestion:", question)

    print("\n--- OPENAI ---")
    ask_openai(question)

    print("\n--- CLAUDE ---")
    ask_claude(question, "You are a helpful assistant.")
