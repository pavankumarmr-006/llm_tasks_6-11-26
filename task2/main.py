
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load API keys
load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

claude_client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

prompt = "Explain Artificial Intelligence in simple words."


# -------- OPENAI NON-STREAMING --------

print("\n--- OPENAI NON-STREAMING ---")

start = time.time()

response = openai_client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=200
)

openai_answer = response.choices[0].message.content

end = time.time()

print("Answer:", openai_answer)
print("Time to first output:", round(end - start, 2), "seconds")
print("Total time:", round(end - start, 2), "seconds")


# -------- OPENAI STREAMING --------

print("\n--- OPENAI STREAMING ---")

start = time.time()
first_token = None
chunks = []

try:
    response = openai_client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        stream=True
    )

    for chunk in response:
        text = chunk.choices[0].delta.content

        if text:
            if first_token is None:
                first_token = time.time() - start

            chunks.append(text)
            print(text, end="", flush=True)

except Exception as e:
    print("\nError:", e)

openai_stream_answer = "".join(chunks)

end = time.time()

print("\nFirst token time:", round(first_token, 2) if first_token is not None else "No token")
print("Total streaming time:", round(end - start, 2), "seconds")

print("Answers match:", openai_answer == openai_stream_answer)


# -------- CLAUDE NON-STREAMING --------

print("\n--- CLAUDE NON-STREAMING ---")

start = time.time()

try:
    response = claude_client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
        system="You are a helpful assistant."
    )

    claude_answer = response.content[0].text

    end = time.time()

    print("Answer:", claude_answer)
    print("Time to first output:", round(end - start, 2), "seconds")
    print("Total time:", round(end - start, 2), "seconds")

except Exception as e:
    claude_answer = ""
    print("Claude Error:", e)


# -------- CLAUDE STREAMING --------

print("\n--- CLAUDE STREAMING ---")

start = time.time()
first_token = None
chunks = []

try:
    with claude_client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
        system="You are a helpful assistant."
    ) as stream:

        for text in stream.text_stream:

            if first_token is None:
                first_token = time.time() - start

            chunks.append(text)
            print(text, end="", flush=True)

except Exception as e:
    print("\nStream interrupted:", e)

claude_stream_answer = "".join(chunks)

end = time.time()

print("\nFirst token time:", round(first_token, 2) if first_token is not None else "No token")
print("Total streaming time:", round(end - start, 2), "seconds")

print("Answers match:", claude_answer == claude_stream_answer)


print("\n--- TASK COMPLETED ---")
