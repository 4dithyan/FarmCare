"""
Gemini AI service for Cardamom disease detection.
"""

import google.generativeai as genai
from django.conf import settings
import logging
import base64
import re

import io
from PIL import Image

logger = logging.getLogger(__name__)


def analyze_cardamom_image(image_path: str, history_context: str = "None") -> dict:
    """
    Analyze a cardamom image using Google Gemini API with mandatory constraints.
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-3-flash-preview')

        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Resize image for much faster performance
        try:
            img = Image.open(io.BytesIO(image_data))
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Max dimension 800px
            max_size = 800
            if max(img.size) > max_size:
                ratio = max_size / float(max(img.size))
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
            # Save back to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            image_data = buffer.getvalue()
        except Exception as resize_err:
            logger.warning(f"Resizing failed, using original: {resize_err}")

        # Determine MIME type
        ext = image_path.lower().split('.')[-1]
        mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
        mime_type = mime_map.get(ext, 'image/jpeg')

        prompt = f"""System Role: You are a senior Agricultural Pathologist specialized in Elettaria cardamomum (Small Cardamom) and Amomum subulatum (Large Cardamom) in India.

Task: Analyze the provided plant image.

Constraint 1: Species Identification (Mandatory)
Verify if the image contains a cardamom plant (leaf, capsule, stem, or rhizome).

If NOT Cardamom: Stop all analysis. Output ONLY a valid JSON: {{"error": "species_mismatch", "message": "This image is not a cardamom plant. Please upload a clear photo of your cardamom crop for analysis."}}.

Constraint 2: History Context (Memory)
[[HISTORY_CONTEXT]]: {history_context}

If [[HISTORY_CONTEXT]] is "None": Provide a fresh, comprehensive diagnosis.

If [[HISTORY_CONTEXT]] contains data: This means the user has uploaded this image before.
Consistency: You MUST identify the same disease as mentioned in the context.
Advanced Expansion: You MUST add a section called **EXPERT DEEP DIVE:** with new, advanced technical advice (e.g., specific soil pH adjustment, shade-tree density management, or bio-control agents like Trichoderma harzianum) that was NOT in the previous result.

Output Format (if Cardamom):
For EACH section, provide the info first in English, then in Malayalam (മലയാളം). Use simple, step-by-step terms. 
DO NOT use markdown symbols like ** or + or # inside the descriptions (only for section headers).

**VALIDATION:**
- IS_CARDAMOM: Yes
- Image Content: [Briefly describe what you see]

**DISEASE DETECTION:**
- Disease Name: [Specific name or "Healthy"]
- Confidence Level: [High/Medium/Low]
- Affected Parts: [leaves/pods/stem/roots etc.]

**SYMPTOMS OBSERVED:**
English: 1. ...
Malayalam: 1. ...

**DIAGNOSIS:**
English: ...
Malayalam: ...

**RECOMMENDED MEDICINES/TREATMENTS:**
English: ...
Malayalam: ...

**DOSAGE & APPLICATION:**
English: Step 1: ...
Malayalam: സ്റ്റെപ്പ് 1: ...

**PRECAUTIONS:**
English: ...
Malayalam: ...

**SEVERITY:**
[Critical/High/Medium/Low]

**EXPERT DEEP DIVE:**
[English and Malayalam technical details for repeat uploads only]
"""

        image_part = {
            'mime_type': mime_type,
            'data': base64.b64encode(image_data).decode('utf-8')
        }

        response = model.generate_content([prompt, image_part])
        response_text = response.text

        # Check for JSON error (species mismatch)
        if '"error": "species_mismatch"' in response_text or response_text.strip().startswith('{'):
            try:
                import json
                # Clean potential markdown from json
                cleaned_json = re.sub(r'```json\n?|\n?```', '', response_text).strip()
                error_data = json.loads(cleaned_json)
                return {
                    'is_cardamom': False,
                    'gemini_response': error_data.get('message', 'Species mismatch.'),
                    'success': False
                }
            except:
                pass

        # Parse the standard response
        is_cardamom = extract_field(response_text, 'IS_CARDAMOM')
        
        result = {
            'is_cardamom': is_cardamom.lower() == 'yes',
            'disease_detected': extract_field(response_text, 'Disease Name'),
            'confidence_level': extract_field(response_text, 'Confidence Level'),
            'severity': extract_field(response_text, 'SEVERITY'),
            'medicines': extract_block(response_text, 'RECOMMENDED MEDICINES/TREATMENTS'),
            'dosage': extract_block(response_text, 'DOSAGE & APPLICATION'),
            'precautions': extract_block(response_text, 'PRECAUTIONS'),
            'symptoms': extract_block(response_text, 'SYMPTOMS OBSERVED'),
            'diagnosis': extract_block(response_text, 'DIAGNOSIS'),
            'expert_deep_dive': extract_block(response_text, 'EXPERT DEEP DIVE'),
            'gemini_response': response_text,
            'success': True if is_cardamom.lower() == 'yes' else False,
        }

        return result

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {
            'is_cardamom': False,
            'disease_detected': 'Analysis Failed',
            'confidence_level': 'N/A',
            'gemini_response': f'Error during analysis: {str(e)}',
            'success': False,
        }


def extract_field(text: str, field_name: str) -> str:
    """Extract a specific field value from formatted Gemini response."""
    try:
        pattern = rf'{re.escape(field_name)}:\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Remove markdown bold markers
            value = value.replace('**', '').replace('*', '').strip()
            return value
        return 'Unknown'
    except Exception:
        return 'Unknown'


def extract_block(text: str, field_name: str) -> str:
    """Extract a block of text following a heading with better flexibility."""
    try:
        # Matches **HEADING:** or **HEADING** followed by newline, then captures until next ** or end
        pattern = rf'\*\*{re.escape(field_name)}:?\*\*\n?(.*?)(?=\n\n\*\*|\n---\n|$)'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Clean up leading/trailing dashes if captured
            content = re.sub(r'^---\s*', '', content)
            return content
        return ''
    except Exception:
        return ''


def get_disease_keywords() -> list:
    """Common cardamom diseases for matching with recommendations."""
    return [
        'katte disease', 'mosaic disease', 'capsule rot',
        'rhizome rot', 'damping off', 'leaf blight',
        'thrips', 'stem borer', 'root grub', 'caterpillar',
        'anthracnose', 'fusarium wilt', 'pythium',
        'phytophthora', 'healthy', 'viral infection',
    ]
