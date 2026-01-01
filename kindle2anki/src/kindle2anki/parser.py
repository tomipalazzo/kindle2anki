"""Parser for Kindle My Clippings.txt file."""

from typing import NamedTuple
from datetime import datetime


class KindleEntry(NamedTuple):
    """Represents a single entry from Kindle clippings."""
    book_title: str
    author: str
    content: str
    entry_type: str  # "Highlight" or "Note"
    location: str
    timestamp: str


def parse_clippings(file_path: str) -> list[KindleEntry]:
    """
    Parse My Clippings.txt file and return list of entries.
    
    The file format is:
    Book Title (Author Name)
    - Your [Highlight|Note] on page X | Location Y-Z | Added on [Date]
    
    [Content text]
    ==========
    """
    entries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by the separator
    raw_entries = content.split('==========')
    
    for raw_entry in raw_entries:
        lines = raw_entry.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # Parse book and author
        book_line = lines[0].strip()
        if not book_line or '(' not in book_line:
            continue
        
        # Extract title and author
        if '(' in book_line and ')' in book_line:
            book_title = book_line[:book_line.rfind('(')].strip()
            author = book_line[book_line.rfind('(') + 1:book_line.rfind(')')].strip()
        else:
            continue
        
        # Parse metadata line
        meta_line = lines[1].strip()
        if not meta_line.startswith('- Your'):
            continue
        
        # Extract entry type, location, timestamp
        entry_type = "Highlight" if "Highlight" in meta_line else "Note"
        
        # Extract location (e.g., "Location 37-37")
        location = ""
        if "Location" in meta_line:
            location_start = meta_line.find("Location") + len("Location")
            location_end = meta_line.find("|", location_start)
            if location_end == -1:
                location_end = len(meta_line)
            location = meta_line[location_start:location_end].strip()
        
        # Extract timestamp
        timestamp = ""
        if "Added on" in meta_line:
            timestamp = meta_line[meta_line.find("Added on") + len("Added on"):].strip()
        
        # Get content (everything after metadata line, excluding empty lines at end)
        clipping_content = '\n'.join(lines[2:]).strip()
        if not clipping_content:
            continue
        
        entry = KindleEntry(
            book_title=book_title,
            author=author,
            content=clipping_content,
            entry_type=entry_type,
            location=location,
            timestamp=timestamp
        )
        entries.append(entry)
    
    return entries


def extract_words_from_entries(entries: list[KindleEntry]) -> list[dict]:
    """
    Extract word entries from clippings.
    Assumes that highlights are typically single words and notes are definitions/translations.
    """
    word_entries = []
    
    # Group by book and location to find word-definition pairs
    for i, entry in enumerate(entries):
        if entry.entry_type == "Highlight":
            # Try to find a corresponding note (definition)
            definition = None
            for j in range(i + 1, min(i + 3, len(entries))):
                if (entries[j].entry_type == "Note" and 
                    entries[j].book_title == entry.book_title and
                    entries[j].location == entry.location):
                    definition = entries[j].content
                    break
            
            word_entries.append({
                'word': entry.content.strip(),
                'definition': definition or "",
                'context': entry.content,
                'book_title': entry.book_title,
                'author': entry.author,
                'location': entry.location,
                'timestamp': entry.timestamp
            })
    
    return word_entries
