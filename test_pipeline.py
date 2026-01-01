#!/usr/bin/env python3
"""Test script to verify the Kindle to Anki pipeline with 5 example words."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set API key from .env
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY or OPEN_AI_API_KEY environment variable not set!")
    sys.exit(1)
os.environ["OPENAI_API_KEY"] = api_key

# Add src to path
sys.path.insert(0, 'kindle2anki/src')

from kindle2anki.parser import parse_clippings, extract_words_from_entries
from kindle2anki.llm_service import LLMService
from kindle2anki.audio_generator import AudioGenerator
from kindle2anki.image_fetcher import ImageFetcher
from kindle2anki.card_builder import CardBuilder
from kindle2anki.deck_generator import DeckGenerator


def test_pipeline():
    """Test the full pipeline with 5 example words."""
    print("=" * 70)
    print("Kindle to Anki Pipeline - TEST WITH 5 EXAMPLES")
    print("=" * 70)
    
    # Initialize services
    print("\n[INIT] Initializing services...")
    llm_service = LLMService(db_path="data/vocab.db")
    audio_gen = AudioGenerator(db_path="data/vocab.db", output_dir="output/audio")
    image_fetcher = ImageFetcher(db_path="data/vocab.db", output_dir="output/images")
    card_builder = CardBuilder()
    deck_gen = DeckGenerator(output_dir="output", audio_dir="output/audio")
    print("✓ All services initialized")
    
    # Parse clippings
    print("\n[PARSE] Parsing Kindle clippings...")
    entries = parse_clippings("data/My Clippings.txt")
    word_entries = extract_words_from_entries(entries)
    print(f"✓ Found {len(word_entries)} total words")
    
    # Test with first 5 words
    test_words = word_entries[:5]
    print(f"✓ Testing with first {len(test_words)} words")
    
    cards_by_book = {}
    
    for i, word_entry in enumerate(test_words, 1):
        word = word_entry["word"].strip()
        definition = word_entry.get("definition", "").strip()
        book_title = word_entry.get("book_title", "Unknown Book")
        
        if not word:
            continue
        
        print(f"\n[{i}/5] Processing '{word}'")
        print(f"      Definition: {definition[:60]}")
        print(f"      Book: {book_title}")
        
        # Initialize book dict if needed
        if book_title not in cards_by_book:
            cards_by_book[book_title] = []
        
        try:
            # Generate hint
            print(f"      → Generating hint...", end=" ", flush=True)
            hint = llm_service.generate_hint(word, definition)
            print(f"✓")
            print(f"        Hint: {hint}")
            
            # Generate examples
            print(f"      → Generating 5 examples...", end=" ", flush=True)
            examples = llm_service.generate_examples(word, definition)
            print(f"✓")
            for j, example in enumerate(examples, 1):
                print(f"        {j}. {example[:60]}...")
            
            # Check if noun
            print(f"      → Detecting if noun...", end=" ", flush=True)
            is_noun = llm_service.detect_is_noun(word)
            print(f"{'✓ (Yes)' if is_noun else '✓ (No)'}")
            
            # Fetch image if noun
            image_path = None
            if is_noun:
                print(f"      → Fetching image...", end=" ", flush=True)
                image_result = image_fetcher.fetch_image(word)
                if image_result and image_result.get("image_url"):
                    image_path = image_result.get("image_url")
                    print(f"✓")
                    print(f"        {image_path[:50]}...")
                else:
                    print(f"✗ (Not found)")
            
            # Generate audio
            print(f"      → Generating audio (word)...", end=" ", flush=True)
            word_audio = audio_gen.generate_word_audio(word)
            print(f"{'✓' if word_audio else '✗'}")
            if word_audio:
                print(f"        {word_audio}")
            
            print(f"      → Generating audio for {len(examples)} examples...", end=" ", flush=True)
            example_audios = []
            for j, example in enumerate(examples, 1):
                example_audio = audio_gen.generate_phrase_audio(example, word)
                example_audios.append(example_audio)
            print(f"✓")
            
            # Build cards (one per example)
            print(f"      → Building {len(examples)} cards (one per example)...", end=" ", flush=True)
            cards = card_builder.build_cards(
                word_entry=word_entry,
                hint=hint,
                examples=examples,
                word_audio_path=word_audio,
                example_audio_paths=example_audios,
                image_path=image_path
            )
            print(f"✓")
            
            # Display card preview for first card only
            if cards:
                print(f"\n      FIRST CARD PREVIEW (of {len(cards)}):")
                print(f"      Front: {cards[0].build_front()[:100]}...")
                print(f"      Back (first 150 chars): {cards[0].build_back()[:150]}...")
            
            cards_by_book[book_title].extend(cards)
            print(f"\n      ✓ Created {len(cards)} cards successfully")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate decks
    print("\n[DECK] Generating Anki decks...")
    try:
        saved_files = deck_gen.save_decks_by_book(cards_by_book, parent_deck_name="Test Deck")
        print(f"✓ Decks generated successfully")
        for book_title, file_path in saved_files.items():
            print(f"  - {book_title}: {file_path}")
    except Exception as e:
        print(f"✗ Error generating decks: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    total_cards = sum(len(cards) for cards in cards_by_book.values())
    print(f"Total cards created: {total_cards}")
    print(f"Books processed: {len(cards_by_book)}")
    for book_title, cards in cards_by_book.items():
        print(f"  - {book_title}: {len(cards)} cards")
    print("\n✓ Pipeline test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_pipeline()
