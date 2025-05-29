"""
Speech-to-Text Service for MAMA-AI Voice Integration

This service provides speech-to-text conversion capabilities for voice recordings
from Africa's Talking. It supports multiple providers:
- Google Speech-to-Text API
- Azure Speech Services
- OpenAI Whisper API
- Fallback to simulated responses for testing

Created: 2024
Author: MAMA-AI Development Team
"""

import os
import requests
import base64
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime


class SpeechToTextService:
    """Service for converting speech recordings to text"""
    
    def __init__(self):
        """Initialize the Speech-to-Text service"""
        self.provider = os.getenv('SPEECH_TO_TEXT_PROVIDER', 'whisper')  # whisper, google, azure, mock
        self.google_api_key = os.getenv('GOOGLE_SPEECH_API_KEY')
        self.azure_speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.azure_speech_region = os.getenv('AZURE_SPEECH_REGION')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
    def convert_recording_to_text(self, recording_url: str, language: str = 'en-US') -> Dict[str, Any]:
        """
        Convert speech recording to text
        
        Args:
            recording_url: URL of the audio recording
            language: Language code (e.g., 'en-US', 'sw-KE' for Kiswahili)
            
        Returns:
            Dict with transcript, confidence, and metadata
        """
        try:
            # Download the audio file
            audio_data = self._download_audio(recording_url)
            if not audio_data:
                return self._create_error_response("Failed to download audio")
            
            # Convert based on provider
            if self.provider == 'whisper' and self.openai_api_key:
                return self._convert_with_whisper(audio_data, language)
            elif self.provider == 'google' and self.google_api_key:
                return self._convert_with_google(audio_data, language)
            elif self.provider == 'azure' and self.azure_speech_key:
                return self._convert_with_azure(audio_data, language)
            else:
                # Fallback to mock response for testing
                return self._convert_with_mock(recording_url, language)
                
        except Exception as e:
            print(f"Error in speech-to-text conversion: {str(e)}")
            return self._create_error_response(f"Speech conversion error: {str(e)}")
    
    def _download_audio(self, recording_url: str) -> Optional[bytes]:
        """Download audio file from URL"""
        try:
            response = requests.get(recording_url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download audio: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading audio: {str(e)}")
            return None
    
    def _convert_with_whisper(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Convert speech to text using OpenAI Whisper API"""
        try:
            # Map language codes
            whisper_lang = self._map_language_to_whisper(language)
            
            # Prepare the request
            files = {
                'file': ('audio.wav', audio_data, 'audio/wav'),
                'model': (None, 'whisper-1'),
                'language': (None, whisper_lang),
                'response_format': (None, 'json'),
                'temperature': (None, '0')
            }
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}'
            }
            
            # Make the API request
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                files=files,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transcript': result.get('text', ''),
                    'confidence': 0.95,  # Whisper doesn't provide confidence scores
                    'language': language,
                    'provider': 'whisper',
                    'duration': None,
                    'processing_time': None
                }
            else:
                print(f"Whisper API error: {response.status_code} - {response.text}")
                return self._create_error_response(f"Whisper API error: {response.status_code}")
                
        except Exception as e:
            print(f"Whisper conversion error: {str(e)}")
            return self._create_error_response(f"Whisper error: {str(e)}")
    
    def _convert_with_google(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Convert speech to text using Google Speech-to-Text API"""
        try:
            # Encode audio data
            audio_content = base64.b64encode(audio_data).decode('utf-8')
            
            # Prepare the request
            request_data = {
                'config': {
                    'encoding': 'WEBM_OPUS',  # Adjust based on actual format
                    'sampleRateHertz': 16000,
                    'languageCode': language,
                    'enableAutomaticPunctuation': True,
                    'enableWordTimeOffsets': False,
                    'model': 'latest_long'
                },
                'audio': {
                    'content': audio_content
                }
            }
            
            # Make the API request
            response = requests.post(
                f'https://speech.googleapis.com/v1/speech:recognize?key={self.google_api_key}',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(request_data),
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                
                if results and 'alternatives' in results[0]:
                    alternative = results[0]['alternatives'][0]
                    return {
                        'success': True,
                        'transcript': alternative.get('transcript', ''),
                        'confidence': alternative.get('confidence', 0.0),
                        'language': language,
                        'provider': 'google',
                        'duration': None,
                        'processing_time': None
                    }
                else:
                    return self._create_error_response("No speech detected")
            else:
                print(f"Google Speech API error: {response.status_code} - {response.text}")
                return self._create_error_response(f"Google API error: {response.status_code}")
                
        except Exception as e:
            print(f"Google Speech conversion error: {str(e)}")
            return self._create_error_response(f"Google error: {str(e)}")
    
    def _convert_with_azure(self, audio_data: bytes, language: str) -> Dict[str, Any]:
        """Convert speech to text using Azure Speech Services"""
        try:
            # Map language code for Azure
            azure_lang = self._map_language_to_azure(language)
            
            # Prepare headers
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_speech_key,
                'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
                'Accept': 'application/json'
            }
            
            # Build the URL
            url = f'https://{self.azure_speech_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'
            params = {
                'language': azure_lang,
                'format': 'detailed'
            }
            
            # Make the API request
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('RecognitionStatus') == 'Success':
                    return {
                        'success': True,
                        'transcript': result.get('DisplayText', ''),
                        'confidence': result.get('NBest', [{}])[0].get('Confidence', 0.0),
                        'language': language,
                        'provider': 'azure',
                        'duration': result.get('Duration'),
                        'processing_time': None
                    }
                else:
                    return self._create_error_response(f"Azure recognition failed: {result.get('RecognitionStatus')}")
            else:
                print(f"Azure Speech API error: {response.status_code} - {response.text}")
                return self._create_error_response(f"Azure API error: {response.status_code}")
                
        except Exception as e:
            print(f"Azure Speech conversion error: {str(e)}")
            return self._create_error_response(f"Azure error: {str(e)}")
    
    def _convert_with_mock(self, recording_url: str, language: str) -> Dict[str, Any]:
        """Mock speech-to-text for testing purposes"""
        # Intelligent mock responses based on likely content
        mock_responses = [
            "I need help with my pregnancy",
            "I'm feeling some pain in my stomach",
            "When is my next appointment",
            "I have some concerns about my baby",
            "I want to check my pregnancy status",
            "I need emergency help",
            "Can you help me with nutrition advice",
            "I'm experiencing morning sickness",
            "I want to schedule an appointment",
            "What should I expect this week"
        ]
        
        # Use a simple hash to make responses consistent for testing
        import hashlib
        hash_input = recording_url + language
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        selected_response = mock_responses[hash_value % len(mock_responses)]
        
        # Translate to appropriate language if needed
        if language.startswith('sw'):  # Kiswahili
            kiswahili_responses = {
                "I need help with my pregnancy": "Nahitaji msaada na uja uzito wangu",
                "I'm feeling some pain in my stomach": "Nahisi maumivu katika tumbo langu",
                "When is my next appointment": "Ni lini miadi yangu ijayo",
                "I have some concerns about my baby": "Nina wasiwasi kuhusu mtoto wangu",
                "I want to check my pregnancy status": "Nataka kuangalia hali ya uja uzito wangu",
                "I need emergency help": "Nahitaji msaada wa dharura",
                "Can you help me with nutrition advice": "Je, unaweza kunisaidia na ushauri wa lishe",
                "I'm experiencing morning sickness": "Ninasikia kichefuchefu cha asubuhi",
                "I want to schedule an appointment": "Nataka kupanga miadi",
                "What should I expect this week": "Ni nini ninachopaswa kutarajia wiki hii"
            }
            selected_response = kiswahili_responses.get(selected_response, selected_response)
        
        return {
            'success': True,
            'transcript': selected_response,
            'confidence': 0.85,
            'language': language,
            'provider': 'mock',
            'duration': '5.2s',
            'processing_time': '0.8s',
            'note': 'This is a mock response for testing. Enable real speech-to-text by setting up API keys.'
        }
    
    def _map_language_to_whisper(self, language: str) -> str:
        """Map language codes to Whisper language codes"""
        mapping = {
            'en-US': 'en',
            'en-GB': 'en',
            'en': 'en',
            'sw-KE': 'sw',
            'sw': 'sw',
            'ki-KE': 'sw',  # Kiswahili alternative
        }
        return mapping.get(language, 'en')
    
    def _map_language_to_azure(self, language: str) -> str:
        """Map language codes to Azure Speech language codes"""
        mapping = {
            'en-US': 'en-US',
            'en-GB': 'en-GB',
            'en': 'en-US',
            'sw-KE': 'sw-KE',
            'sw': 'sw-KE',
            'ki-KE': 'sw-KE',
        }
        return mapping.get(language, 'en-US')
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'success': False,
            'transcript': '',
            'confidence': 0.0,
            'language': 'en',
            'provider': self.provider,
            'error': error_message,
            'duration': None,
            'processing_time': None
        }
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [
            {'code': 'en-US', 'name': 'English (US)', 'native': 'English'},
            {'code': 'en-GB', 'name': 'English (UK)', 'native': 'English'},
            {'code': 'sw-KE', 'name': 'Kiswahili (Kenya)', 'native': 'Kiswahili'},
        ]
    
    def test_service(self) -> Dict[str, Any]:
        """Test the speech-to-text service configuration"""
        status = {
            'provider': self.provider,
            'whisper_configured': bool(self.openai_api_key) if self.provider == 'whisper' else False,
            'google_configured': bool(self.google_api_key) if self.provider == 'google' else False,
            'azure_configured': bool(self.azure_speech_key and self.azure_speech_region) if self.provider == 'azure' else False,
            'fallback_available': True,  # Mock is always available
            'supported_languages': len(self.get_supported_languages())
        }
        
        return status


# Example usage and testing
if __name__ == "__main__":
    # Initialize the service
    stt_service = SpeechToTextService()
    
    # Test the service configuration
    print("🎙️ Speech-to-Text Service Test")
    print("=" * 50)
    
    status = stt_service.test_service()
    print(f"Provider: {status['provider']}")
    print(f"Configured: {status.get(f'{status['provider']}_configured', False)}")
    print(f"Supported Languages: {status['supported_languages']}")
    
    # Test with a mock recording URL
    print("\n🧪 Testing with mock recording...")
    result = stt_service.convert_recording_to_text(
        recording_url="https://example.com/test-recording.wav",
        language="en-US"
    )
    
    print(f"Success: {result['success']}")
    print(f"Transcript: {result['transcript']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Provider: {result['provider']}")
    
    if result.get('note'):
        print(f"Note: {result['note']}")
