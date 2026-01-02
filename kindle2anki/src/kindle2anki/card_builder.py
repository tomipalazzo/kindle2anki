"""Card builder for Anki flashcards."""

from typing import Optional


class AnkiCard:
    """Represents an Anki flashcard."""
    
    def __init__(self, 
                 word: str,
                 hint: str,
                 full_definition: str,
                 example: str,
                 example_index: int = 1,
                 word_audio_path: Optional[str] = None,
                 example_audio_path: Optional[str] = None,
                 image_path: Optional[str] = None,
                 book_title: str = "",
                 location: str = ""):
        """Initialize an Anki card with a single example."""
        self.word = word
        self.hint = hint
        self.full_definition = full_definition
        self.example = example
        self.example_index = example_index
        self.word_audio_path = word_audio_path
        self.example_audio_path = example_audio_path
        self.image_path = image_path
        self.book_title = book_title
        self.location = location
    
    def get_cloze_blank(self) -> str:
        """Get the word in cloze format: C_T (first and last letter)."""
        if len(self.word) <= 2:
            return self.word
        return f"{self.word[0]}{'_' * (len(self.word) - 2)}{self.word[-1]}"
    
    def apply_cloze_to_text(self, text: str) -> str:
        """Apply cloze blank to word within text."""
        cloze = self.get_cloze_blank()
        # Replace the word (case-insensitive) with cloze blank
        import re
        # Try to match the exact word first
        pattern = re.compile(re.escape(self.word), re.IGNORECASE)
        result = pattern.sub(cloze, text, count=1)
        return result
    
    def build_front(self) -> str:
        """Build the front of the card with example + cloze blank + hint."""
        # Apply cloze blank to the example
        cloze_example = self.apply_cloze_to_text(self.example)
        
        # Front: Example sentence (centered) + Hint (blue, larger, centered)
        front = '<div style="text-align: center; font-size: 20px;">'
        front += f'"{cloze_example}"<br/><br/>'
        front += f'<span style="color: #0066cc; font-size: 24px; font-weight: bold;">{self.hint}</span>'
        front += '</div>'
        
        # Add image if available (only on first card)
        if self.image_path and self.example_index == 1:
            if self.image_path.startswith("http"):
                front += f'<br/><img src="{self.image_path}" style="max-width: 300px; max-height: 300px;">'
            else:
                front += f'<br/><img src="{self.image_path}" style="max-width: 300px; max-height: 300px;">'
        
        return front
    
    def build_back(self) -> str:
        """Build the back of the card with word and audio buttons."""
        # Back: Word centered, large, bold
        back = '<div style="text-align: center;">'
        back += f'<h2 style="font-size: 32px; margin: 20px 0;">{self.word}</h2>'
        
        # Add audio references (using just filenames)
        back += '<div style="margin-top: 20px;">'
        if self.word_audio_path:
            word_audio_filename = self.word_audio_path.split('/')[-1]
            back += f'[sound:{word_audio_filename}]&nbsp;&nbsp;'
        if self.example_audio_path:
            example_audio_filename = self.example_audio_path.split('/')[-1]
            back += f'[sound:{example_audio_filename}]'
        back += '</div>'
        
        back += '</div>'
        
        # Add book context at bottom
        if self.book_title:
            back += f'<br/><small style="text-align: center;">From: <i>{self.book_title}</i>'
            if self.location:
                back += f' ({self.location})'
            back += '</small>'
        
        return back
    
    def to_dict(self) -> dict:
        """Convert card to dictionary for genanki."""
        return {
            "front": self.build_front(),
            "back": self.build_back(),
            "word": self.word,
            "book_title": self.book_title
        }


class CardBuilder:
    """Builder for creating Anki cards from word entries."""
    
    @staticmethod
    def build_cards(word_entry: dict,
                    hint: str,
                    examples: list[str],
                    word_audio_path: Optional[str] = None,
                    example_audio_paths: Optional[list[str]] = None,
                    image_path: Optional[str] = None) -> list[AnkiCard]:
        """
        Build multiple Anki cards from a word entry - one card per example.
        Each card has a different example on the front and matching audio on the back.
        
        Args:
            word_entry: Dict with word, definition, context, book_title, location
            hint: Synonym or hint for the cloze blank
            examples: List of 5 example sentences
            word_audio_path: Path to audio file for the word
            example_audio_paths: List of paths to audio files for each example
            image_path: Path to image file (for nouns, used only on first card)
        
        Returns:
            List of AnkiCard instances (one per example)
        """
        if example_audio_paths is None:
            example_audio_paths = [None] * len(examples)
        
        cards = []
        for i, example in enumerate(examples):
            card = AnkiCard(
                word=word_entry.get("word", ""),
                hint=hint,
                full_definition=word_entry.get("definition", word_entry.get("context", "")),
                example=example,
                example_index=i + 1,
                word_audio_path=word_audio_path,
                example_audio_path=example_audio_paths[i] if i < len(example_audio_paths) else None,
                image_path=image_path if i == 0 else None,  # Image only on first card
                book_title=word_entry.get("book_title", ""),
                location=word_entry.get("location", "")
            )
            cards.append(card)
        
        return cards