# conversation_generator.py
import json
import csv
import random
from google import genai
from google.genai import types
import os
from datetime import datetime
import argparse

class ScamConversationGenerator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.scam_types = [
            "bank_fraud",
            "tech_support",
            "lottery_winner", 
            "relative_emergency",
            "government_official",
            "job_offer"
        ]
        
        self.languages = {
            "hindi": "Generate conversation in Hindi only",
            "hinglish": "Generate conversation in Hinglish (Hindi-English mix)",
            "english": "Generate conversation in English only"
        }
        
    def generate_conversation(self, scam_type, language, conversation_id):
        """Generate a scam conversation using Gemini API"""
        
        prompt = self._build_prompt(scam_type, language)
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    max_output_tokens=2000,
                )
            )
            
            return self._parse_response(response.text, conversation_id, scam_type, language)
            
        except Exception as e:
            print(f"Error generating conversation: {e}")
            return None
    
    def _build_prompt(self, scam_type, language):
        """Build the prompt for Gemini"""

        base_prompts = {
                "bank_fraud": {
                "english": """Generate a realistic and natural phone conversation between a bank fraud scammer and a victim. 
        The scammer pretends to be from the victim's bank security department, claiming there’s suspicious activity on their account.

        SCAMMER: (professional, persuasive, urgent; may ask for OTP/account details)
        VICTIM: (initially cautious; may become convinced or remain skeptical)

        Requirements:
        - Use only spoken dialogue lines. Do NOT include stage directions, sound descriptions, or action descriptions inside the dialogue (for example: do not use *rustling sounds*, (reading out the card number slowly), [sigh], or any bracketed/asterisked actions).
        - Short natural hesitations like "um", "uh", "…", and short pauses written as ellipses are allowed inside spoken lines.
        - Speaker labels must always be the labels VICTIM and SCAMMER (do NOT label speakers by any provided name).
        - If either person introduces their own name in speech (e.g., "This is Rahul from the bank" or "I'm Mr. Mehta"), then those names may be used naturally inside later spoken lines (e.g., "Mr. Mehta, could you confirm..."). Do NOT replace the line label with those names — lines must still start with VICTIM: or SCAMMER:.
        - Alternate speakers line-by-line. Include at least 8–10 exchanges.
        - End the conversation naturally (victim realizes it's a scam, refuses, gives info, hangs up upset, etc.). Do not end abruptly or with instructions.""",

                    "hindi": """बैंक धोखाधड़ी स्कैमर और पीड़ित के बीच एक वास्तविक फोन वार्तालाप उत्पन्न करें। 
        स्कैमर बैंक सुरक्षा विभाग होने का दावा करता है और कहता है कि खाते में संदिग्ध गतिविधि है।

        नियम:
        - केवल बोली हुई संवाद पंक्तियाँ लिखें। संवाद में स्टेज डायरेक्शन, आवाज़ के वर्णन या क्रियाओं का वर्णन न डालें (उदाहरण: *rustling sounds*, (reading out the card number slowly), [sigh] इत्यादि न लिखें)।
        - "um", "uh", "..." जैसी संक्षिप्त हिचकियाँ या विराम स्वीकार्य हैं।
        - स्पीकर लेबल हमेशा VICTIM और SCAMMER रहें; नामों से लाइन लेबल मत बदलें।
        - यदि कोई स्पीकर अपने नाम का परिचय देता है, तो वह नाम बाद की बोली में प्राकृतिक रूप से उपयोग किया जा सकता है पर लाइन की शुरुआत VICTIM: या SCAMMER: ही होनी चाहिए।
        - स्पीकर्स बारी-बारी बोलें, कम से कम 8–10 विनिमय शामिल करें।
        - बातचीत का अंत स्वाभाविक रूप से करें।""",

                    "hinglish": """Generate a realistic Hinglish phone conversation between a bank fraud scammer and a victim.

        Rules:
        - Include only spoken dialogue lines. Do NOT include stage directions or sound/action descriptions like *rustling sounds* or (reading out the card number slowly).
        - Short spoken hesitations ("um", "uh", "…") are allowed.
        - Always label lines with VICTIM: and SCAMMER: only.
        - If a name is spoken by a character, that name can be used naturally later inside speech, but do NOT replace the line label with that name.
        - Alternate speakers line-by-line and produce at least 8–10 exchanges.
        - End naturally (victim refuses, realises, or call ends emotionally)."""
                },

                "tech_support": {
                    "english": """Generate a tech support scam conversation where the scammer claims the victim's computer has a virus.

        Rules:
        - Only spoken dialogue lines. Forbid stage directions, sound cues, or action descriptions in parentheses or asterisks.
        - Short hesitations allowed ("um", "uh", "...").
        - Labels must remain VICTIM: and SCAMMER:.
        - If names are spoken, reuse them inside dialogue (do not use them as labels).
        - Alternate lines and end naturally (refusal, agreement, or hang up).""",

                    "hindi": """... (same rules as above in Hindi)""",

                    "hinglish": """... (same rules as above in Hinglish)"""
                }
            }

        language_instruction = self.languages.get(language, "")
        scam_prompt = base_prompts.get(scam_type, {}).get(language, base_prompts["bank_fraud"]["english"])

        return f"""{language_instruction}

    {scam_prompt}

    FORMAT (follow exactly):
    VICTIM: [spoken dialogue — no stage directions or sound descriptions]
    SCAMMER: [spoken dialogue — no stage directions or sound descriptions]
    VICTIM: ...
    SCAMMER: ...

    Ensure strict alternation, natural flow, allowed brief hesitations (um, uh, ...), and a natural, complete ending."""

    def _parse_response(self, response_text, conversation_id, scam_type, language):
        """Parse the Gemini response into structured format"""
        
        lines = response_text.strip().split('\n')
        segments = []
        current_speaker = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('VICTIM:') or line.startswith('SCAMMER:'):
                # Save previous segment
                if current_speaker and current_text:
                    segments.append({
                        'speaker': current_speaker,
                        'role': 'victim' if current_speaker == 'VICTIM' else 'scammer',
                        'text': ' '.join(current_text)
                    })
                
                # Start new segment
                current_speaker = 'VICTIM' if line.startswith('VICTIM:') else 'SCAMMER'
                current_text = [line.split(':', 1)[1].strip()]
            elif current_speaker and line:
                current_text.append(line)
        
        # Add the last segment
        if current_speaker and current_text:
            segments.append({
                'speaker': current_speaker,
                'role': 'victim' if current_speaker == 'VICTIM' else 'scammer',
                'text': ' '.join(current_text)
            })
        
        return {
            'file_id': conversation_id,
            'scam_type': scam_type,
            'language': language,
            'segments': segments,
            'num_speakers': 2,
            'speaker_roles': ['victim', 'scammer'],
            'timestamp': datetime.now().isoformat()
        }

def main():
    parser = argparse.ArgumentParser(description='Generate scam conversations using Google Gemini API')
    parser.add_argument('--api-key', required=True, help='Google AI Studio API key')
    parser.add_argument('--num-conversations', type=int, default=5, help='Number of conversations to generate')
    parser.add_argument('--output-dir', default='generated_conversations', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    generator = ScamConversationGenerator(args.api_key)
    
    conversations_metadata = []
    
    for i in range(args.num_conversations):
        # Randomly select scam type and language
        scam_type = random.choice(generator.scam_types)
        language = random.choice(list(generator.languages.keys()))
        
        conversation_id = f"conv_{i+1:03d}"
        print(f"Generating conversation {i+1}/{args.num_conversations}: {scam_type} in {language}")
        
        conversation = generator.generate_conversation(scam_type, language, conversation_id)
        
        if conversation:
            # Save individual conversation JSON
            output_file = os.path.join(args.output_dir, f"{conversation_id}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, indent=2, ensure_ascii=False)
            
            # Add to metadata
            conversations_metadata.append({
                'file_id': conversation_id,
                'filename': f"{conversation_id}.json",
                'scam_type': scam_type,
                'language': language,
                'num_speakers': 2,
                'speaker_roles': 'victim,scammer',
                'timestamp': conversation['timestamp']
            })
            
            print(f"Saved: {output_file}")
    
    # Save metadata CSV
    metadata_file = os.path.join(args.output_dir, 'metadata.csv')
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['file_id', 'filename', 'scam_type', 'language', 'num_speakers', 'speaker_roles', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(conversations_metadata)
    
    print(f"\nGenerated {args.num_conversations} conversations in '{args.output_dir}'")
    print(f"Metadata saved: {metadata_file}")

if __name__ == "__main__":
    main()