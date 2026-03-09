import google.generativeai as genai
import os
from django.conf import settings
import django

# Setup django to access settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmcare.settings')
django.setup()

genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
