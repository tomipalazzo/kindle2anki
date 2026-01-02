# Kindle2Anki - Turn Your Kindle Highlights Into Flashcards

## What Is This?

**Kindle2Anki** is a tool that automatically converts words and phrases you've highlighted in your Kindle books into interactive study flashcards using **Anki** (a popular flashcard app).

### What You Need to Know

- **Kindle Highlights** = Words or phrases you saved while reading on your Kindle
- **Anki** = A free flashcard app that helps you study and remember things
- **Flashcards** = Cards with a question on one side and an answer on the other

This tool takes your Kindle highlights and creates beautiful, interactive flashcards that include:
- ✓ Definitions of words
- ✓ Hints to help you remember
- ✓ Real examples of how to use the word
- ✓ Audio pronunciation (how to say the word)
- ✓ Images (for nouns/objects)

All organized by book!

---

## Getting Started - Step by Step

### Prerequisites (One-Time Setup)

You'll need:

1. **Python** - A programming language that powers this tool
   - Download from [python.org](https://www.python.org/downloads/) (version 3.8 or newer)
   - During installation, **make sure to check "Add Python to PATH"**

2. **An OpenAI API Key** - This is used to generate definitions, hints, and examples
   - Go to [openai.com](https://platform.openai.com/api-keys)
   - Create a free account (you get $5 in free credits)
   - Create a new API key and save it somewhere safe

3. **Git** (optional but recommended) - To download this tool
   - Download from [git-scm.com](https://git-scm.com/)

### Installation (One-Time)

1. **Get the code**
   - If you have Git: Open Terminal and run:
     ```bash
     git clone https://github.com/tomipalazzo/kindle2anki.git
     cd kindle2anki
     ```
   - If you don't have Git: Download as ZIP from GitHub and extract it

2. **Install dependencies**
   - Open Terminal (Mac/Linux) or Command Prompt (Windows) in the kindle2anki folder
   - Run:
     ```bash
     pip install -e .
     ```
   - Wait for everything to install (you'll see a lot of text)

3. **Set up your API key**
   - In the kindle2anki folder, create a file named `.env`
   - Open it in a text editor and add:
     ```
     OPENAI_API_KEY=your_key_here
     ```
   - Replace `your_key_here` with your actual OpenAI API key
   - Save and close

---

## How to Use It

### Step 1: Get Your Kindle Highlights

Your Kindle highlights are stored in a file called "My Clippings.txt". To get this file:

**On Amazon Kindle (via USB)**
1. Connect your Kindle to your computer with a USB cable
2. Open the Kindle folder on your computer
3. Look for a file named `My Clippings.txt`
4. Copy this file to the `data` folder inside kindle2anki

**On Amazon.com website**
1. Go to [read.amazon.com](https://read.amazon.com)
2. Open a book you've read
3. Go to "Your Highlights" (usually in the menu)
4. Select all highlights, copy them, and paste into a text file
5. Save as `My Clippings.txt` in the `data` folder

### Step 2: Run the Tool

1. **Open Terminal** (or Command Prompt on Windows) in the kindle2anki folder
2. **Run** this command:
   ```bash
   python -m kindle2anki.main
   ```
3. **Wait** - The tool will:
   - Read your highlights
   - Look up definitions
   - Generate helpful hints and examples
   - Create audio files of pronunciations
   - Find images for nouns
   - Create Anki deck files

This might take a while depending on how many words you have. You'll see progress messages as it goes.

### Step 3: Import Into Anki

1. **Download Anki** from [ankiweb.net](https://ankiweb.net/download)
2. **Open Anki**
3. **Look for your deck files** - They'll be in the `output` folder with `.apkg` extension
   - They're organized by book (e.g., "The Hobbit.apkg")
4. **Double-click** on a `.apkg` file to import it into Anki
5. **Start studying!**

---

## Understanding Your Flashcards

Each flashcard has:

**Front (the question):**
- An example sentence using the word
- Audio button to hear the example

**Back (the answer):**
- The word definition
- A helpful hint
- More example sentences
- Images (if it's a noun)
- Audio pronunciation of the word

---

## Troubleshooting

### "Command not found: python"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH" during installation

### "OPENAI_API_KEY not set"
- Your `.env` file doesn't exist or is missing the API key
- Make sure the `.env` file is in the kindle2anki folder
- Double-check the API key is correct

### "My Clippings.txt not found"
- Make sure the file is in the `data` folder
- Check the filename is exactly `My Clippings.txt` (case matters!)

### "Error: rate limit exceeded"
- You've hit OpenAI's rate limit
- Wait a few minutes and try again
- Consider upgrading your OpenAI account if you have many words

### "No cards were created"
- Your clippings file might not have any words in the expected format
- Check that "My Clippings.txt" has actual highlight entries

---

## Tips for Best Results

1. **Be selective with highlights** - Quality over quantity. Highlight words you actually want to learn.

2. **Add context** - When highlighting a word, make sure the surrounding context is included.

3. **Start small** - Test with 5-10 words first to see if you like the output

4. **Review regularly** - Anki flashcards work best when you study a little bit every day

5. **Customize in Anki** - After importing, you can edit cards in Anki if you want to change anything

---

## FAQ

**Q: Will this work with my Kindle app on my phone?**
A: Yes! The Kindle app also saves highlights to "My Clippings.txt"

**Q: Can I edit the flashcards after importing?**
A: Yes! Anki lets you edit any card. Just be aware your edits won't be lost if you re-run the tool.

**Q: How much does this cost?**
A: The tool itself is free. OpenAI's API costs money after your free trial, but it's very cheap (less than $0.01 per 1000 words typically).

**Q: Can I create multiple Anki decks from different books?**
A: Yes! The tool automatically creates separate decks for each book you've read.

**Q: What if I want to rerun the tool with more words?**
A: No problem! Delete the old `.apkg` files and run the tool again. It will create fresh decks.

---

## Need Help?

- Check the issues on [GitHub](https://github.com/tomipalazzo/kindle2anki/issues)
- Make sure all dependencies are installed correctly
- Check your internet connection (the tool needs it for API calls)

---

## What's Next?

Once you've set up your flashcards in Anki:
1. Use the Anki app on your phone/computer
2. Study for 10-15 minutes daily
3. Anki will remind you of words right before you're likely to forget them
4. Watch your vocabulary grow!

Happy learning! 📚