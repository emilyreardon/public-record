# Public Record

A handmade mobile of democracy's primary sources. Each element carries an NFC tag: tap it with a phone to read an excerpt, answer a prompt about public life today, and, if you like, send your words to your elected representatives through Resistbot. A small open AI model running on a laptop in the room answers each submission with an "echo": a clause from the historical record that speaks to what you wrote.

Project page and AI model card: https://emilyreardon.org/public-record.html

## What's here

| | |
|---|---|
| `submit.html` | The page a phone opens from an NFC tag: excerpt, prompt, submission |
| `monitor.html` | The shared screen in the room showing the growing record |
| `ai_server.py` | Local AI server: finds the related clause and writes the echo |
| `chunk_and_embed.py` | Splits the corpus into passages and indexes them for retrieval |
| `public-record-corpus/` | The 137 source documents as text (US public domain) |
| `corpus-data.json` | Excerpts and prompts shown for each document |
| `print/` | Print templates for the NFC labels on the mobile |
| `tools/` | Scripts used to gather and clean the corpus, kept for transparency |
| `start.sh`, `stop.sh`, `setup_autostart.sh` | Start and stop the installation |
| `supabase_setup.sql` | Database table for submissions |

## How it runs

Everything that touches visitors' words runs locally: [Ollama](https://ollama.com) with OLMo 3 (from the nonprofit Allen Institute for AI) for the echo and `nomic-embed-text` for retrieval. Setup steps are in `AI_SETUP.md`.

## Credits

Concept, curation, design and fabrication: Emily Reardon. Code written with help from Claude (Anthropic).

Code: MIT License (see `LICENSE`). The corpus documents are US federal works and other public-domain texts.
