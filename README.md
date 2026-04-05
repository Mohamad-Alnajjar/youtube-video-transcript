# YouTube → Japanese Study Doc

A Streamlit app that fetches YouTube transcripts and reformats them into clean, study-ready Japanese documents using Claude AI.

## Features

- **Fetch transcripts** from any YouTube video URL or video ID
- **Select subtitle language** from all available options (manual or auto-generated)
- **Raw transcript** export with optional timestamps → `.docx`
- **AI-powered study version** — Claude reformats raw, unpunctuated transcript text into properly punctuated Japanese sentences → `.docx` and `.pdf`

## Demo

![App screenshot placeholder](https://via.placeholder.com/800x400?text=App+Screenshot)

## Getting Started

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/youtube-video-transcript.git
cd youtube-video-transcript

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file with your API key:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

> **Note:** This file is listed in `.gitignore` and will never be committed.

#### Optional: YouTube Proxy (for Streamlit Cloud deployments)

When deployed on Streamlit Cloud, YouTube may block requests from the server IP. Add [Webshare](https://webshare.io) proxy credentials to avoid this:

```toml
WEBSHARE_PROXY_USERNAME = "your-username"
WEBSHARE_PROXY_PASSWORD = "your-password"
```

### Run the app

```bash
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage

1. Paste a YouTube URL or video ID into the input field
2. Select the subtitle language from the dropdown
3. Choose options:
   - **Timestamps in raw doc** — include `[0:00]` markers in the raw export
   - **Generate study version** — use Claude to reformat the transcript
4. Click **Generate Transcript**
5. Download the raw `.docx` and/or the study `.docx` / `.pdf`

## Project Structure

```
youtube-video-transcript/
├── .devcontainer/          # GitHub Codespaces configuration
├── .streamlit/
│   └── secrets.toml        # API keys (not committed)
├── .venv/                  # Virtual environment (not committed)
├── .gitignore
├── requirements.txt
├── README.md
└── streamlit_app.py
```

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web app framework |
| `anthropic` | Claude AI for transcript formatting |
| `youtube-transcript-api` | Fetch YouTube transcripts |
| `python-docx` | Generate `.docx` files |
| `reportlab` | Generate `.pdf` files with Japanese font support |

## Deploying to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file to `streamlit_app.py`
4. Add your secrets under **Settings → Secrets**:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

## License

MIT
