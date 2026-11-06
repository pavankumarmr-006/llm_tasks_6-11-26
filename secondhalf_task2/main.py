
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import tiktoken
import sqlite3
import json
from datetime import datetime, date

app = FastAPI()

client = OpenAI()

# Read config file
with open("config.json", "r") as file:
    config = json.load(file)

MODEL = config["model"]
INPUT_PRICE = config["input_price"]
OUTPUT_PRICE = config["output_price"]
CONTEXT_LIMIT = config["context_limit"]
DAILY_BUDGET = config["daily_budget"]


# Create database
def create_database():

    conn = sqlite3.connect("usage.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            model TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            cost REAL
        )
    """)

    conn.commit()
    conn.close()


create_database()


# 1. Count tokens
def count_tokens(messages, model):

    encoding = tiktoken.encoding_for_model(model)

    total = 0

    for message in messages:

        total += 4

        total += len(
            encoding.encode(message["content"])
        )

    total += 2

    return total


# 2. Calculate cost
def calculate_cost(prompt_tokens, completion_tokens):

    input_cost = (prompt_tokens / 1000000) * INPUT_PRICE

    output_cost = (completion_tokens / 1000000) * OUTPUT_PRICE

    total_cost = input_cost + output_cost

    return total_cost


# 3. Save usage in database
def save_usage(model, prompt_tokens, completion_tokens, cost):

    conn = sqlite3.connect("usage.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usage
        (timestamp, model, prompt_tokens, completion_tokens, cost)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        model,
        prompt_tokens,
        completion_tokens,
        cost
    ))

    conn.commit()

    conn.close()


# 4. Get today's total cost
def get_today_cost():

    conn = sqlite3.connect("usage.db")

    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
        SELECT SUM(cost)
        FROM usage
        WHERE DATE(timestamp) = ?
    """, (today,))

    result = cursor.fetchone()[0]

    conn.close()

    return result or 0


# 5. Chat API

@app.post("/chat")
def chat():

    messages = [
        {
            "role": "user",
            "content": "Explain Python in simple words"
        }
    ]

    try:
        # Count estimated tokens
        estimated_tokens = count_tokens(messages, MODEL)

        print("Estimated tokens:", estimated_tokens)

        # Check context limit
        if estimated_tokens > CONTEXT_LIMIT:
            raise HTTPException(
                status_code=400,
                detail="Context limit exceeded"
            )

        # Check daily budget
        if get_today_cost() >= DAILY_BUDGET:
            raise HTTPException(
                status_code=429,
                detail="Daily budget exceeded"
            )

        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        # Get actual token usage
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        # Calculate cost
        cost = calculate_cost(
            prompt_tokens,
            completion_tokens
        )

        # Save usage
        save_usage(
            MODEL,
            prompt_tokens,
            completion_tokens,
            cost
        )

        return {
            "reply": response.choices[0].message.content,
            "estimated_tokens": estimated_tokens,
            "actual_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost": round(cost, 6)
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# 6. Get today's usage
@app.get("/usage")
def usage():

    conn = sqlite3.connect("usage.db")

    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
        SELECT
        SUM(prompt_tokens + completion_tokens),
        SUM(cost)
        FROM usage
        WHERE DATE(timestamp) = ?
    """, (today,))

    result = cursor.fetchone()

    conn.close()

    return {
        "date": today,
        "total_tokens": result[0] or 0,
        "total_cost": round(result[1] or 0, 6)
    }
