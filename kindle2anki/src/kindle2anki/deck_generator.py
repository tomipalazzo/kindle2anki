"""Anki deck generator using genanki."""

import os
import glob
import random
import genanki
from typing import Optional


class DeckGenerator:
    """Generate Anki decks from cards, organized by book."""
    
    def __init__(self, output_dir: str = "output", audio_dir: str = "output/audio"):
        """Initialize deck generator."""
        self.output_dir = output_dir
        self.audio_dir = audio_dir
        os.makedirs(output_dir, exist_ok=True)
        self.model = self._create_model()
    
    def _create_model(self) -> genanki.Model:
        """Create Anki note model for vocabulary cards."""
        return genanki.Model(
            model_id=random.randrange(1 << 30, 1 << 31),
            name="Kindle Vocabulary Card",
            fields=[
                {"name": "Front"},
                {"name": "Back"},
                {"name": "Word"},
                {"name": "BookTitle"}
            ],
            templates=[
                {
                    "name": "Card",
                    "qfmt": "{{Front}}",
                    "afmt": "{{FrontSide}}<hr id=answer>{{Back}}"
                }
            ]
        )
    
    def create_deck_from_cards(self, 
                               cards: list,
                               deck_name: str,
                               book_title: Optional[str] = None) -> genanki.Deck:
        """
        Create a genanki Deck from a list of cards.
        
        Args:
            cards: List of AnkiCard instances
            deck_name: Name for the deck
            book_title: Optional book title for organizing
        
        Returns:
            genanki.Deck instance
        """
        # Create deck with unique ID based on deck name
        deck_id = abs(hash(deck_name)) % (1 << 30)
        deck = genanki.Deck(deck_id, deck_name)
        
        # Add notes to deck
        for card in cards:
            card_dict = card.to_dict()
            note = genanki.Note(
                model=self.model,
                fields=[
                    card_dict["front"],
                    card_dict["back"],
                    card_dict["word"],
                    book_title or card_dict.get("book_title", "")
                ]
            )
            deck.add_note(note)
        
        return deck
    
    def save_deck(self, deck: genanki.Deck, filename: str) -> str:
        """
        Save a deck to an .apkg file with audio media files.
        
        Args:
            deck: genanki.Deck instance
            filename: Output filename (without extension)
        
        Returns:
            Path to saved file
        """
        output_path = os.path.join(self.output_dir, f"{filename}.apkg")
        
        # Create package and add all audio files
        package = genanki.Package(deck)
        
        # Add all audio files from audio directory
        if os.path.exists(self.audio_dir):
            audio_files = glob.glob(os.path.join(self.audio_dir, "*.mp3"))
            for audio_file in audio_files:
                package.media_files.append(audio_file)
        
        package.write_to_file(output_path)
        return output_path
    
    def save_decks_by_book(self, 
                          cards_by_book: dict,
                          parent_deck_name: str = "Kindle Vocabulary") -> dict:
        """
        Save multiple decks, one per book.
        
        Args:
            cards_by_book: Dict mapping book titles to lists of AnkiCard instances
            parent_deck_name: Name of the parent deck
        
        Returns:
            Dict mapping book titles to saved file paths
        """
        saved_files = {}
        
        for book_title, cards in cards_by_book.items():
            if not cards:
                continue
            
            # Create deck name
            safe_book_name = "".join(
                c for c in book_title 
                if c.isalnum() or c in (' ', '-', '_')
            ).strip()
            safe_book_name = safe_book_name.replace(' ', '_')
            
            deck_name = f"{parent_deck_name}::{safe_book_name}"
            
            # Create and save deck
            deck = self.create_deck_from_cards(
                cards,
                deck_name,
                book_title
            )
            
            saved_path = self.save_deck(deck, safe_book_name)
            saved_files[book_title] = saved_path
            
            print(f"Created deck for '{book_title}' with {len(cards)} cards: {saved_path}")
        
        return saved_files
