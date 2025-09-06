import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def analyze_image_with_gemini(image_path):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Free tier model
    with open(image_path, 'rb') as img:
        response = model.generate_content([
            "Detect if there is garbage or open drainage in this image. Describe what you see.",
            {"mime_type": "image/jpeg", "data": img.read()}  # Assume JPEG; adjust if needed
        ])
    return response.text