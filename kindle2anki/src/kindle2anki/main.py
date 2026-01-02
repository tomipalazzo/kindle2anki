"""Main orchestration script for Kindle to Anki conversion."""

import os
import sys
from pathlib import Path
from typing import Optional

from parser import parse_clippings, extract_words_from_entries
from llm_service import LLMService
from audio_generator import AudioGenerator
from image_fetcher import ImageFetcher
from card_builder import CardBuilder
from deck_generator import DeckGenerator
from dotenv import load_dotenv
load_dotenv()


def process_clippings_to_anki(
    clippings_file: str = "data/My Clippings.txt",
    db_path: str = "data/vocab.db",
    output_dir: str = "output",
    max_words: Optional[int] = None
) -> dict:
    """
    Main pipeline to convert Kindle clippings to Anki decks.
    
    Args:
        clippings_file: Path to My Clippings.txt
        db_path: Path to vocab.db
        output_dir: Directory to save .apkg files
        max_words: Maximum number of words to process (for testing)
    
    Returns:
        Dict with stats about processing
    """
    print("=" * 60)
    print("Kindle to Anki Card Generator")
    print("=" * 60)
    
    # Initialize services
    llm_service = LLMService(db_path=db_path)
    audio_gen = AudioGenerator(db_path=db_path, output_dir=os.path.join(output_dir, "audio"))
    image_fetcher = ImageFetcher(db_path=db_path, output_dir=os.path.join(output_dir, "images"))
    card_builder = CardBuilder()
    deck_gen = DeckGenerator(output_dir=output_dir, audio_dir=os.path.join(output_dir, "audio"))
    
    # Parse clippings
    print("\n[1/5] Parsing Kindle clippings...")
    entries = parse_clippings(clippings_file)
    word_entries = extract_words_from_entries(entries)
    print(f"Found {len(word_entries)} word entries")
    
    if max_words:
        word_entries = word_entries[:max_words]
        print(f"Processing first {len(word_entries)} words")
    
    # Process words
    print("\n[2/5] Processing words with LLM...")
    cards_by_book = {}
    
    for i, word_entry in enumerate(word_entries, 1):
        word = word_entry["word"].strip()
        definition = word_entry.get("definition", "").strip()
        book_title = word_entry.get("book_title", "Unknown Book")
        
        if not word:
            continue
        
        print(f"  [{i}/{len(word_entries)}] Processing '{word}'...")
        
        # Initialize book dict if needed
        if book_title not in cards_by_book:
            cards_by_book[book_title] = []
        
        try:
            # Generate hint
            hint = llm_service.generate_hint(word, definition)
            print(f"    - Hint: {hint}")
            
            # Generate examples
            examples = llm_service.generate_examples(word, definition)
            print(f"    - Generated {len(examples)} examples")
            
            # Check if noun and fetch image
            is_noun = llm_service.detect_is_noun(word)
            image_path = None
            if is_noun:
                print(f"    - Noun detected, fetching image...")
                image_result = image_fetcher.fetch_image(word)
                if image_result and image_result.get("image_url"):
                    image_path = image_result.get("image_url")
                    print(f"    - Image: {image_path[:60]}...")
                elif image_result and image_result.get("image_path"):
                    image_path = image_result.get("image_path")
                    print(f"    - Image: {image_path}")
            
            # Generate audio for word
            print(f"    - Generating audio for word...")
            word_audio = audio_gen.generate_word_audio(word)
            
            # Generate audio for each example
            print(f"    - Generating audio for {len(examples)} examples...")
            example_audios = []
            for j, example in enumerate(examples, 1):
                example_audio = audio_gen.generate_phrase_audio(example, word)
                example_audios.append(example_audio)
                print(f"      • Example {j} audio: {'✓' if example_audio else '✗'}")
            
            # Build cards (one per example with different example on front)
            cards = card_builder.build_cards(
                word_entry=word_entry,
                hint=hint,
                examples=examples,
                word_audio_path=word_audio,
                example_audio_paths=example_audios,
                image_path=image_path
            )
            
            cards_by_book[book_title].extend(cards)
            print(f"    ✓ Created {len(cards)} cards ({len(examples)} examples)")
            
        except Exception as e:
            print(f"    ✗ Error processing word: {e}")
            continue
    
    # Generate decks
    print("\n[3/5] Generating Anki decks...")
    saved_files = deck_gen.save_decks_by_book(cards_by_book)
    
    # Print summary
    print("\n[4/5] Summary:")
    print(f"Total books: {len(cards_by_book)}")
    for book_title, cards in cards_by_book.items():
        print(f"  - {book_title}: {len(cards)} cards")
    
    print("\n[5/5] Generated files:")
    for book_title, file_path in saved_files.items():
        print(f"  - {book_title}: {file_path}")
    
    print("\n" + "=" * 60)
    print("Conversion complete!")
    print("=" * 60)
    
    return {
        "total_words_processed": len([c for cards in cards_by_book.values() for c in cards]),
        "books": {title: len(cards) for title, cards in cards_by_book.items()},
        "saved_files": saved_files
    }


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        sys.exit(1)
    
    # Get optional max_words argument for testing
    max_words = None
    if len(sys.argv) > 1:
        try:
            max_words = int(sys.argv[1])
        except ValueError:
            pass
    
    # Run conversion
    result = process_clippings_to_anki(max_words=max_words)
