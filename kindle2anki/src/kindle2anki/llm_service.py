"""OpenAI API service for generating examples, hints, and detecting parts of speech."""

import os
import sqlite3
import json
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()



class LLMService:
    """Service for OpenAI API interactions with caching in vocab.db."""
    
    def __init__(self, db_path: str = "data/vocab.db"):
        """Initialize LLM service with database connection."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_path = db_path
        self._ensure_cache_table()
    
    def _ensure_cache_table(self):
        """Ensure the LLM cache table exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS LLM_CACHE (
                    id TEXT PRIMARY KEY,
                    word TEXT NOT NULL,
                    cache_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    timestamp INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS llm_cache_word_type 
                ON LLM_CACHE (word, cache_type)
            """)
            conn.commit()
    
    def _get_cache_key(self, word: str, cache_type: str) -> str:
        """Generate a unique cache key."""
        return f"{word.lower()}_{cache_type}"
    
    def _get_cached_result(self, word: str, cache_type: str) -> Optional[str]:
        """Get cached result from database."""
        cache_key = self._get_cache_key(word, cache_type)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT result FROM LLM_CACHE WHERE id = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            if row:
                return row[0]
        return None
    
    def _cache_result(self, word: str, cache_type: str, result: str):
        """Cache result in database."""
        cache_key = self._get_cache_key(word, cache_type)
        import time
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO LLM_CACHE (id, word, cache_type, result, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (cache_key, word, cache_type, result, int(time.time()))
            )
            conn.commit()
    
    def detect_is_noun(self, word: str) -> bool:
        """
        Detect if word is a noun using OpenAI API with caching.
        Returns True if noun, False otherwise.
        """
        # Check cache first
        cached = self._get_cached_result(word, "is_noun")
        if cached is not None:
            return cached.lower() == "true"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Is the word '{word}' a noun (person, place, or thing)? Answer only 'true' or 'false'."
                }],
                temperature=0,
                max_tokens=5
            )
            
            result = response.choices[0].message.content.strip().lower()
            is_noun = result == "true"
            
            # Cache the result
            self._cache_result(word, "is_noun", str(is_noun).lower())
            
            return is_noun
        except Exception as e:
            print(f"Error detecting noun for '{word}': {e}")
            return False
    
    def generate_examples(self, word: str, definition: str = "") -> list[str]:
        """
        Generate 5 example sentences for a word using OpenAI API with caching.
        """
        # Check cache first
        cached = self._get_cached_result(word, "examples")
        if cached is not None:
            return json.loads(cached)
        
        try:
            context = f" (definition: {definition})" if definition else ""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"""Generate exactly 5 natural English example sentences using the word '{word}'{context}.
                    
Format your response as a JSON array of strings, like this:
["sentence 1", "sentence 2", "sentence 3", "sentence 4", "sentence 5"]

Only output the JSON array, no other text."""
                }],
                temperature=0.7,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            # Parse JSON array
            examples = json.loads(result_text)
            if not isinstance(examples, list):
                examples = [result_text]
            
            # Ensure we have exactly 5 examples
            examples = examples[:5] + [""] * (5 - len(examples))
            examples = examples[:5]
            
            # Cache the result
            self._cache_result(word, "examples", json.dumps(examples))
            
            return examples
        except Exception as e:
            print(f"Error generating examples for '{word}': {e}")
            return [f"{word} is used in a sentence."] * 5
    
    def generate_hint(self, word: str, definition: str = "") -> str:
        """
        Generate a synonym or hint for the cloze blank using OpenAI API with caching.
        """
        # Check cache first
        cached = self._get_cached_result(word, "hint")
        if cached is not None:
            return cached
        
        try:
            context = f" (definition: {definition})" if definition else ""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"""Provide a very brief hint or synonym for the word '{word}'{context}.
                    
The hint should be short (2-5 words) and help someone guess the word.
Only output the hint, nothing else."""
                }],
                temperature=0.7,
                max_tokens=50
            )
            
            hint = response.choices[0].message.content.strip()
            
            # Cache the result
            self._cache_result(word, "hint", hint)
            
            return hint
        except Exception as e:
            print(f"Error generating hint for '{word}': {e}")
            return definition or word
