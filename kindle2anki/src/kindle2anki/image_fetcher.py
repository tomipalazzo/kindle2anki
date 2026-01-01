"""Image fetching for nouns using web search."""

import os
import sqlite3
from typing import Optional
import requests
from urllib.parse import quote


class ImageFetcher:
    """Fetch images for nouns with caching."""
    
    def __init__(self, db_path: str = "data/vocab.db", output_dir: str = "output/images"):
        """Initialize image fetcher."""
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._ensure_cache_table()
    
    def _ensure_cache_table(self):
        """Ensure the image cache table exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS IMAGE_CACHE (
                    id TEXT PRIMARY KEY,
                    word TEXT NOT NULL,
                    image_path TEXT,
                    image_url TEXT,
                    timestamp INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS image_cache_word 
                ON IMAGE_CACHE (word)
            """)
            conn.commit()
    
    def _get_cache_key(self, word: str) -> str:
        """Generate a unique cache key."""
        return f"{word.lower()}_image"
    
    def _get_cached_image(self, word: str) -> Optional[dict]:
        """Get cached image from database."""
        cache_key = self._get_cache_key(word)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT image_path, image_url FROM IMAGE_CACHE WHERE id = ?",
                (cache_key,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "image_path": row[0],
                    "image_url": row[1]
                }
        return None
    
    def _cache_image(self, word: str, image_path: Optional[str], image_url: Optional[str]):
        """Cache image path and URL in database."""
        cache_key = self._get_cache_key(word)
        import time
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO IMAGE_CACHE (id, word, image_path, image_url, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (cache_key, word, image_path, image_url, int(time.time()))
            )
            conn.commit()
    
    def fetch_image(self, word: str) -> Optional[dict]:
        """
        Fetch an image URL for a noun using a simple web API.
        Returns dict with image_url, or None if not found.
        Note: This implementation returns URLs rather than downloading files
        to keep the system lightweight and avoid large binary files in the repo.
        """
        # Check cache first
        cached = self._get_cached_image(word)
        if cached:
            return cached
        
        try:
            # Try using Unsplash API (no auth needed for basic searches)
            # This is a simple, free solution for getting image URLs
            url = f"https://api.unsplash.com/search/photos?query={quote(word)}&per_page=1&client_id=demo"
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    image_url = data["results"][0].get("urls", {}).get("regular")
                    if image_url:
                        result = {
                            "image_path": None,
                            "image_url": image_url
                        }
                        # Cache result
                        self._cache_image(word, None, image_url)
                        return result
            
            # Cache negative result
            self._cache_image(word, None, None)
            return None
            
        except Exception as e:
            print(f"Error fetching image for '{word}': {e}")
            # Cache negative result
            self._cache_image(word, None, None)
            return None
