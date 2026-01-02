"""Audio generation using OpenAI TTS API."""

import os
import sqlite3
from typing import Optional
from openai import OpenAI


class AudioGenerator:
    """Generate audio files using OpenAI's TTS API with caching."""
    
    def __init__(self, db_path: str = "data/vocab.db", output_dir: str = "output/audio"):
        """Initialize audio generator."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._ensure_cache_table()
    
    def _ensure_cache_table(self):
        """Ensure the audio cache table exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS AUDIO_CACHE (
                    id TEXT PRIMARY KEY,
                    word TEXT NOT NULL,
                    audio_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    timestamp INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS audio_cache_word_type 
                ON AUDIO_CACHE (word, audio_type)
            """)
            conn.commit()
    
    def _get_cache_key(self, word: str, audio_type: str) -> str:
        """Generate a unique cache key."""
        return f"{word.lower()}_{audio_type}"
    
    def _get_cached_audio(self, word: str, audio_type: str) -> Optional[str]:
        """Get cached audio file path from database."""
        cache_key = self._get_cache_key(word, audio_type)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT file_path FROM AUDIO_CACHE WHERE id = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
        return None
    
    def _cache_audio(self, word: str, audio_type: str, file_path: str):
        """Cache audio file path in database."""
        cache_key = self._get_cache_key(word, audio_type)
        import time
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO AUDIO_CACHE (id, word, audio_type, file_path, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (cache_key, word, audio_type, file_path, int(time.time()))
            )
            conn.commit()
    
    def generate_word_audio(self, word: str) -> Optional[str]:
        """
        Generate audio for a word using OpenAI TTS API.
        Returns path to audio file.
        """
        # Check cache first
        cached_path = self._get_cached_audio(word, "word")
        if cached_path and os.path.exists(cached_path):
            return cached_path
        
        try:
            # Generate audio file
            safe_filename = "".join(c for c in word if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_filename = safe_filename.replace(' ', '_')
            file_path = os.path.join(self.output_dir, f"{safe_filename}_word.mp3")
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=word
            )
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Cache the path
            self._cache_audio(word, "word", file_path)
            
            return file_path
        except Exception as e:
            print(f"Error generating audio for word '{word}': {e}")
            return None
    
    def generate_phrase_audio(self, phrase: str, context_word: str) -> Optional[str]:
        """
        Generate audio for a phrase/sentence containing the word.
        Returns path to audio file.
        """
        # Check cache first
        phrase_hash = hash(phrase) % 10000
        cache_key = f"{context_word}_{phrase_hash}"
        cached_path = self._get_cached_audio(cache_key, "phrase")
        if cached_path and os.path.exists(cached_path):
            return cached_path
        
        try:
            # Generate audio file
            safe_filename = "".join(c for c in context_word if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_filename = safe_filename.replace(' ', '_')
            file_path = os.path.join(self.output_dir, f"{safe_filename}_phrase_{phrase_hash}.mp3")
            
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=phrase[:500]  # Limit to 500 chars
            )
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Cache the path
            self._cache_audio(cache_key, "phrase", file_path)
            
            return file_path
        except Exception as e:
            print(f"Error generating audio for phrase: {e}")
            return None
