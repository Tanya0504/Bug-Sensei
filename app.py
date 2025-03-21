from flask import Flask, render_template, request
import os
import google.generativeai as generative_ai
from dotenv import load_dotenv
import logging
from google.api_core.exceptions import GoogleAPIError, InvalidArgument

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env.local
load_dotenv(".env.local")

app = Flask(__name__)

# Set your Gemini API key from the .env.local file
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    logger.error("GOOGLE_API_KEY not found in .env.local")
    raise ValueError("GOOGLE_API_KEY not found in .env.local")

# Configure the Gemini API
generative_ai.configure(api_key=api_key)

# Optional: List available models to debug
def list_available_models():
    try:
        models = generative_ai.list_models()
        available_models = [model.name for model in models]
        logger.info("Available models: %s", available_models)
        return available_models
    except Exception as e:
        logger.error("Error listing models: %s", e)
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    reviewed_code = None
    if request.method == "POST":
        code_to_review = request.form.get("code", "").strip()

        if not code_to_review:
            reviewed_code = "Error: No code provided for review."
        else:
            try:
                # List models for debugging (you can comment this out after confirming)
                list_available_models()

                # Initialize the Gemini model (updated to gemini-1.5-pro)
                model = generative_ai.GenerativeModel('gemini-1.5-pro')
                prompt = f"""Review the following code and provide detailed suggestions for improvement:

```python
{code_to_review}
```"""

                # Generate response from the API
                response = model.generate_content(prompt)
                
                # Check if response is valid
                if response and hasattr(response, 'text'):
                    reviewed_code = response.text
                else:
                    reviewed_code = "Error: Unexpected response format from Gemini API."
                    logger.warning("Invalid response format: %s", response)

            except InvalidArgument as e:
                reviewed_code = f"Invalid input error: {str(e)}"
                logger.error("Invalid input error: %s", e)
            except GoogleAPIError as e:
                reviewed_code = f"API error: {str(e)}"
                logger.error("API error: %s", e)
            except Exception as e:
                reviewed_code = f"Unexpected error during code review: {str(e)}"
                logger.error("Unexpected error: %s", e)

    return render_template("index.html", reviewed_code=reviewed_code)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)