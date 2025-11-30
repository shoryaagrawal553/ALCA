import os
import google.generativeai as genai

# Load API key from environment
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

class GeminiTool:
    def __init__(self):
        self.enabled = GEMINI_KEY is not None and GEMINI_KEY.strip() != ""
        if self.enabled:
            genai.configure(api_key=GEMINI_KEY)
            self.model = genai.GenerativeModel("gemini-pro")

    def explain(self, topic, difficulty, fallback_text):
        """
        Uses Gemini to generate or enhance an explanation.
        Falls back to provided explanation on failure.
        """
        if not self.enabled:
            return fallback_text

        prompt = f"""
Explain the topic "{topic}" at a "{difficulty}" difficulty level.
Use simple language and help the student understand the concept.
Base explanation for context:
{fallback_text}
"""

        try:
            response = self.model.generate_content(prompt)
            if response and hasattr(response, "text"):
                return response.text
            return fallback_text
        except Exception:
            return fallback_text
