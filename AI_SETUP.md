# Public Record — Local AI Server Setup

The AI server powers two features on the success screen:

- **Echo** — after someone submits, find the corpus document most resonant with what they wrote
- **Clusters** — show what themes today's visitors have been responding to

The server runs on the installation laptop, on the local Wi-Fi network shared with the QR-scanning phones.

---

## One-time setup (do this before the installation)

### 1. Install Ollama

Download from https://ollama.com and run the installer.

Then pull the two models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

`nomic-embed-text` is ~270 MB. `llama3.2` is ~2 GB. Pull both over good Wi-Fi before the show.

### 2. Install Python dependencies

```bash
cd ~/public-record-project
pip3 install -r requirements_ai.txt
```

### 3. Set your Supabase credentials

The `/clusters` endpoint reads today's submissions from Supabase. Export these before starting the server:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

Or add them to a `.env` file (don't commit it):

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

Then load it: `export $(cat .env | xargs)`

### 4. Ingest the corpus into ChromaDB

```bash
python3 chunk_and_embed.py
```

This reads all 137 markdown files, embeds them with `nomic-embed-text`, and saves to `./chroma_db/`. Takes ~2 minutes. Only needs to run once unless the corpus changes.

---

## At the installation

### Start the server

```bash
python3 ai_server.py
```

It listens on `0.0.0.0:8000` — all devices on the same Wi-Fi network can reach it.

### Find the laptop's local IP

```bash
ipconfig getifaddr en0
# or
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Example: `192.168.4.12`

### Set AI_URL in submit.html

Open `submit.html`, find this line (~line 393):

```js
AI_URL: '',  // local server during installations e.g. 'http://192.168.4.1:8000'
```

Change it to your laptop's IP:

```js
AI_URL: 'http://192.168.4.12:8000',
```

Push to GitHub Pages. The phones will now call the AI server after each submission.

### Verify it's working

Open a browser on your phone (on the same Wi-Fi) and visit:

```
http://192.168.4.12:8000/health
```

You should see: `{"status":"ok","docs":137,...}`

---

## During the installation

The server logs requests to the terminal. If the `/clusters` section shows offline text, check:

1. Supabase credentials are set
2. The laptop is on the same network as the phones
3. `ollama serve` is running (it usually starts automatically; check with `curl localhost:11434/api/tags`)

The cluster cache refreshes every 2 minutes automatically.

---

## Graceful degradation

If `AI_URL` is empty or the server is unreachable, the form still works completely — the echo and clusters sections just show "AI offline" text. Nothing breaks.

---

## Models used

| Model | Purpose | Size |
|---|---|---|
| `nomic-embed-text` | Embed visitor responses + corpus docs for similarity search | ~270 MB |
| `llama3.2` | Theme clustering (groups today's responses into 3-5 labels) | ~2 GB |

To swap the LLM for a smaller model (e.g. on a slower laptop), set:

```bash
export LLM_MODEL=mistral   # alternative option
```

---

## Re-running after a corpus update

```bash
python3 chunk_and_embed.py --reset   # wipes and rebuilds chroma_db
python3 ai_server.py
```
