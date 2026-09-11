import os
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types

from chatbot_config import BOT_NAME, SYSTEM_PROMPT, MODEL_NAME

load_dotenv()

app = Flask(__name__)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=api_key)


@app.get("/")
def index():
    return render_template(
        "index.html",
        bot_name=BOT_NAME,
        model_name=MODEL_NAME,
    )


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        return jsonify({"reply": response.text or "I could not generate a response."})
    except Exception as exc:
        app.logger.exception("Gemini API request failed")
        return jsonify({"error": "The AI service is temporarily unavailable."}), 502


if __name__ == "__main__":
    app.run()
