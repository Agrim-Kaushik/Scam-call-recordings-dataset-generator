# Scam Conversation Dataset Generator

A complete system for generating synthetic scam-related voice call conversations in Hindi, Hinglish, and English with audio recordings, speaker diarization, and time-aligned transcripts. You can configure the dataset samples as well as the number of samples you want to generate. A few(5) samples have already been provided.

## 📁 Project Structure
    scam_dataset_project/
    ├── conversation_generator.py # Step 1: Generate text conversations
    ├── audio_generator.py # Step 2: Convert to audio with TTS
    ├── requirements.txt # Python dependencies
    ├── generated_conversations/ # Output from step 1 (JSON files)
    │ ├── conv_001.json
    │ ├── conv_002.json
    │ └── metadata.csv
    ├── audio_dataset/ # Output from step 2 (final dataset)
    │ ├── conv_001/
    │ │ ├── segment_001.wav
    │ │ ├── segment_002.wav
    │ │ ├── conv_001_diarization.json
    │ │ └── conv_001_transcript.csv
    │ ├── conv_002/
    │ └── dataset_metadata.csv
    └── README.md
    
## 🚀 Quick Start

### 1. Installation
1.1 Clone or create project directory
```bash
mkdir scam_dataset_project
cd scam_dataset_project
```
1.2 Install dependencies
```bash
pip install -r requirements.txt
```
  
### 2. Get API key
Get a free Google AI Studio API key from: 
```bash
https://aistudio.google.com/
```

### 3. Generate Conversations
  ```bash
  python generate_conversations.py --api-key "YOUR_GOOGLE_API_KEY" --num-conversations 10 --output-dir generated_conversations
  ```
- --api-key: Your Google AI Studio API key (required)
- --num-conversations: Number of conversations to generate (default: 5)
- --output-dir: Output directory for JSON files (default: generated_conversations)

4. Generate Audio
```bash
python generate_audio.py --input-dir generated_conversations --output-dir audio_dataset --audio-format wav
```
- --input-dir: Directory containing conversation JSON files (required) 
- --output-dir: Output directory for audio dataset (default: audio_dataset)  
- --audio-format: Audio format - wav or mp3 (default: wav) 

## 🔧 Code Documentation

### 1. conversation_generator.py

Uses **Google Gemini API** to generate realistic, domain-specific scam conversations.

**Supported Scam Types:**
- bank_fraud - Fake bank security calls  
- tech_support - Fake tech support scams  
- lottery_winner - Fake lottery winning scams  
- relative_emergency - Fake emergency calls pretending to be relatives  
- government_official - Fake government official calls  
- job_offer - Fake job offer scams  

**Supported Languages:**
- hindi - Pure Hindi conversations  
- hinglish - Hindi-English mixed conversations  
- english - Pure English conversations  

### 2. audio_generator.py

Converts text-based conversations to audio using **Microsoft Edge TTS** with distinct voices for scammer and victim.

**Voice Assignment Logic:**
- Automatically assigns different genders to victim and scammer  
- Uses language-appropriate neural voices  
- Applies role-based speech characteristics  
  - Scammers speak faster / more urgently  
  - Victims speak calmer and slower  

## 📊 Output Formats

A few sample outputs (5) are provided with associated metadata for easy inspection.

## 🎯 Technical Specifications

### Audio Quality
- Format: WAV / MP3  
- Sample Rate: 16 kHz (TTS default)  
- Bit Depth: 16-bit  
- Channels: Mono  

### Voice Characteristics
- Victims: Calmer, slower rate (−10% to +5%)  
- Scammers: Faster, urgent tone (+0% to +15%)  
- Gender Balance: Automatically maintained  
- Language Accuracy: Native neural voices for each language  

### Dataset Statistics
- Conversations: Configurable  
- Duration: 30–300 seconds per conversation  
- Segments: 8–15 turns per conversation  
- Balanced across Hindi, Hinglish, and English  

### Audio Quality Checks
- Distinct voices for scammer/victim  
- Natural speech pacing  
- Clear emotional tone  
- No audio artifacts  

### Data Consistency
- Standardized file naming  
- Consistent timestamp formatting  
- Uniform metadata structure  
- Complete diarization coverage
