
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


@app.post("/chat/stream")
async def chat_stream():

    async def generate_text():

        try:
            text = "Hello! Welcome to my LLM streaming application."

            words = text.split()

            for word in words:

                # Send one word at a time
                yield f"data: {word}\n\n"

                await asyncio.sleep(0.5)

            # Final event
            yield "data: [DONE]\n\n"

        except asyncio.CancelledError:
            print("Client disconnected")
            raise

    return StreamingResponse(
        generate_text(),
        media_type="text/event-stream"
    )
