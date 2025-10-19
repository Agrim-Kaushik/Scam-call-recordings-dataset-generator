# audio_generator.py
import json
import os
import asyncio
import edge_tts
import random
import argparse
from datetime import datetime
import csv

class AudioConversationGenerator:
    def __init__(self):
        # Expanded voice list with distinct voices for different roles
        self.voices = {
            "hindi": {
                "victim_male": ["hi-IN-MadhurNeural"],
                "victim_female": ["hi-IN-SwaraNeural"],
                "scammer_male": ["hi-IN-MadhurNeural"],
                "scammer_female": ["hi-IN-SwaraNeural"]
            },
            "hinglish": {
                "victim_male": ["en-IN-PrabhatNeural", "en-IN-SameerNeural"],
                "victim_female": ["en-IN-NeerjaNeural", "en-IN-ShrutiNeural"],
                "scammer_male": ["hi-IN-MadhurNeural", "en-GB-RyanNeural"],
                "scammer_female": ["hi-IN-SwaraNeural", "en-GB-SoniaNeural"]
            },
            "english": {
                "victim_male": ["en-US-AndrewNeural", "en-GB-RyanNeural"],
                "victim_female": ["en-US-AriaNeural", "en-GB-SoniaNeural"],
                "scammer_male": ["en-US-BrianNeural", "en-GB-ThomasNeural"],
                "scammer_female": ["en-US-JennyNeural", "en-GB-HollieNeural"]
            }
        }
        
        # Voice characteristics for more realistic conversations
        self.voice_settings = {
            "victim": {
                "rate": ["-10%", "+0%", "+5%"],
                "volume": ["+0%", "+2%"],
                "pitch": ["+0Hz", "+5Hz"]
            },
            "scammer": {
                "rate": ["+0%", "+10%", "+15%"],
                "volume": ["+0%", "+5%", "+8%"],
                "pitch": ["+0Hz", "+10Hz", "-5Hz"]
            }
        }
        
    async def generate_audio_segment(self, text, voice, output_file, rate="+0%", volume="+0%", pitch="+0Hz"):
        """Generate audio for a single segment using Edge TTS"""
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
            await communicate.save(output_file)
            return True
        except Exception as e:
            print(f"Error generating audio for '{text[:50]}...': {e}")
            # Fallback to basic generation without modifications
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_file)
                return True
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return False
    
    def assign_voices(self, language):
        """Assign distinct voices to victim and scammer"""
        # Assign genders randomly but ensure they're different
        victim_gender = random.choice(["male", "female"])
        scammer_gender = random.choice(["male", "female"])
        
        # Get available voices for each role
        victim_voice_key = f"victim_{victim_gender}"
        scammer_voice_key = f"scammer_{scammer_gender}"
        
        victim_voice = random.choice(self.voices[language][victim_voice_key])
        scammer_voice = random.choice(self.voices[language][scammer_voice_key])
        
        # Ensure voices are different
        while victim_voice == scammer_voice:
            scammer_voice = random.choice(self.voices[language][scammer_voice_key])
        
        # print(f"Assigned voices - Victim ({victim_gender}): {victim_voice}, Scammer ({scammer_gender}): {scammer_voice}")
        
        return victim_voice, scammer_voice, victim_gender, scammer_gender
    
    def get_voice_settings(self, role, gender):
        """Get voice settings based on role and gender"""
        base_settings = self.voice_settings[role]
        
        # Add slight gender-based variations
        if gender == "male":
            pitch_variations = ["-10Hz", "-5Hz", "+0Hz", "+5Hz"]
        else:  # female
            pitch_variations = ["+0Hz", "+5Hz", "+10Hz", "+15Hz"]
        
        return {
            "rate": random.choice(base_settings["rate"]),
            "volume": random.choice(base_settings["volume"]),
            "pitch": random.choice(pitch_variations)
        }
    
    async def generate_conversation_audio(self, conversation_file, output_dir, audio_format="wav"):
        """Generate complete audio conversation from JSON"""
        
        with open(conversation_file, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
        
        file_id = conversation['file_id']
        language = conversation['language']
        
        # Create output directory for this conversation
        conv_dir = os.path.join(output_dir, file_id)
        os.makedirs(conv_dir, exist_ok=True)
        
        # Assign distinct voices
        victim_voice, scammer_voice, victim_gender, scammer_gender = self.assign_voices(language)
        
        print(f"Generating audio for {file_id} in {language}")
        
        audio_segments = []
        diarization_data = []
        
        # Generate audio for each segment
        current_time = 0.0
        
        for i, segment in enumerate(conversation['segments']):
            segment_file = os.path.join(conv_dir, f"segment_{i+1:03d}.{audio_format}")
            
            # Assign voice based on role
            if segment['role'] == 'victim':
                voice = victim_voice
                gender = victim_gender
            else:  # scammer
                voice = scammer_voice
                gender = scammer_gender
            
            # Get voice settings for this role
            settings = self.get_voice_settings(segment['role'], gender)
            
            print(f"  Generating segment {i+1}/{len(conversation['segments'])}: {segment['role']}")
            
            success = await self.generate_audio_segment(
                segment['text'], 
                voice, 
                segment_file,
                rate=settings["rate"],
                volume=settings["volume"],
                pitch=settings["pitch"]
            )
            
            if success:
                # Get actual duration by checking file (rough estimation)
                word_count = len(segment['text'].split())
                segment_duration = max(1.5, word_count * 0.35)
                
                # Add some randomness to make it more natural
                segment_duration *= random.uniform(0.9, 1.2)
                
                audio_segments.append({
                    'file': segment_file,
                    'start': current_time,
                    'end': current_time + segment_duration,
                    'speaker': segment['speaker'],
                    'role': segment['role'],
                    'text': segment['text'],
                })
                
                diarization_data.append({
                    'start': round(current_time, 2),
                    'end': round(current_time + segment_duration, 2),
                    'speaker': segment['speaker'],
                    'role': segment['role'],
                    'text': segment['text'],
                    'voice': voice
                })
                
                current_time += segment_duration + random.uniform(0.3, 1.0)  # Variable pause between segments
        
        # Save diarization JSON
        diarization_json = {
            "file_id": file_id,
            "duration": round(current_time, 2),
            "language": language,
            "scam_type": conversation['scam_type'],
            "voices": {
                "victim": victim_voice,
                "scammer": scammer_voice
            },
            "genders": {
                "victim": victim_gender,
                "scammer": scammer_gender
            },
            "segments": diarization_data
        }
        
        diarization_file = os.path.join(conv_dir, f"{file_id}_diarization.json")
        with open(diarization_file, 'w', encoding='utf-8') as f:
            json.dump(diarization_json, f, indent=2, ensure_ascii=False)
        
        # Save transcript CSV
        transcript_file = os.path.join(conv_dir, f"{file_id}_transcript.csv")
        with open(transcript_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['start', 'end', 'speaker', 'role', 'text', 'voice'])
            for segment in diarization_data:
                writer.writerow([
                    segment['start'], 
                    segment['end'], 
                    segment['speaker'], 
                    segment['role'], 
                    segment['text'],
                    segment['voice']
                ])
        
        return {
            'file_id': file_id,
            'audio_dir': conv_dir,
            'duration_sec': round(current_time, 2),
            'num_segments': len(audio_segments),
            'diarization_file': diarization_file,
            'transcript_file': transcript_file,
            'victim_voice': victim_voice,
            'scammer_voice': scammer_voice
        }

async def main():
    parser = argparse.ArgumentParser(description='Generate audio from scam conversations using Edge TTS')
    parser.add_argument('--input-dir', required=True, help='Directory containing conversation JSON files')
    parser.add_argument('--output-dir', default='audio_dataset', help='Output directory for audio files')
    parser.add_argument('--audio-format', choices=['wav', 'mp3'], default='wav', help='Audio format')
    
    args = parser.parse_args()
    
    generator = AudioConversationGenerator()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all conversation JSON files
    conversation_files = [f for f in os.listdir(args.input_dir) if f.endswith('.json')]
    conversation_files.sort()  # Process in sorted order
    
    print(f"Found {len(conversation_files)} conversation files")
    print("Processing conversations...")
    
    dataset_metadata = []
    
    # Process conversations ONE BY ONE (sequentially)
    for i, conv_file in enumerate(conversation_files, 1):
        print(f"\n[{i}/{len(conversation_files)}] Processing: {conv_file}")
        
        input_path = os.path.join(args.input_dir, conv_file)
        
        result = await generator.generate_conversation_audio(
            input_path, 
            args.output_dir, 
            args.audio_format
        )
        
        if result:
            dataset_metadata.append({
                'file_id': result['file_id'],
                'filename': result['file_id'],
                'duration_sec': result['duration_sec'],
                'num_speakers': 2,
                'speaker_roles': 'victim,scammer',
                'source_type': 'simulated',
                'recording_conditions': 'synthetic_tts',
                'audio_format': args.audio_format,
                'audio_directory': result['audio_dir'],
                'diarization_file': result['diarization_file'],
                'transcript_file': result['transcript_file'],
                'victim_voice': result['victim_voice'],
                'scammer_voice': result['scammer_voice'],
                'notes': 'Generated using Edge TTS with distinct voices'
            })
            
            print(f"✅ Completed: {result['file_id']} ({result['duration_sec']} seconds)")
        else:
            print(f"❌ Failed: {conv_file}")
    
    # Save dataset metadata
    metadata_file = os.path.join(args.output_dir, 'dataset_metadata.csv')
    with open(metadata_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'file_id', 'filename', 'duration_sec', 'num_speakers', 'speaker_roles',
            'source_type', 'recording_conditions', 'audio_format', 'audio_directory',
            'diarization_file', 'transcript_file', 'victim_voice', 'scammer_voice', 'notes'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataset_metadata)
    
    print(f"\nAudio generation completed!")
    print(f"Dataset metadata saved: {metadata_file}")
    print(f"Total conversations processed: {len(dataset_metadata)}")
    print(f"Output directory: {args.output_dir}")

if __name__ == "__main__":
    asyncio.run(main())