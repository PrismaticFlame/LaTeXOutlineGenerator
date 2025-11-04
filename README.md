# PDF to LaTeX Outliner

Generate LaTeX outlines from PDF documents using local AI models. No API keys required!

## Features

- 🤖 Runs completely locally using Ollama
- 📄 Extracts text from PDFs intelligently
- 📝 Generates LaTeX outlines based on your examples
- 🐳 Available as both Python script and Docker container
- 🔒 Private - your documents never leave your machine

## Quick Start (Python - Recommended)

### Prerequisites

1. **Install Ollama**: [ollama.com](https://ollama.com)
   ```bash
   # Mac/Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Windows: Download from ollama.com
   ```

2. **Install Python 3.11+**: [python.org](https://python.org)

### Installation

```bash
# Clone or download this repository
git clone <your-repo-url>
cd pdf-outliner

# Install Python dependencies
pip install -r requirements.txt

# Pull the AI model (one-time, ~2GB download)
ollama pull llama3.2:3b
```

### Usage

1. **Add your example outlines** to the `examples/` directory as `.tex` files
2. **Place your PDF** in the `input/` directory
3. **Run the script**:

```bash
# Basic usage
python outline.py input/your-document.pdf

# Specify custom output location
python outline.py input/your-document.pdf -o my-outline.tex

# Use a different model
python outline.py input/your-document.pdf -m llama3.2:1b
```

Your outline will be generated in `output/your-document_outline.tex`

## Docker Usage

For those who prefer containers or want a completely isolated environment.

### Prerequisites

- Docker installed ([docker.com](https://docker.com))

### Build the Image

```bash
docker build -t pdf-outliner .
```

### Run with Docker

```bash
# Make sure your directories exist
mkdir -p input output examples

# Process a PDF
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/examples:/app/examples \
  pdf-outliner input/your-document.pdf
```

### Even Easier: Docker Compose

```bash
# Build the image
docker-compose build

# Process a PDF
docker-compose run pdf-outliner input/your-document.pdf
```

## Example Outlines (Important!)

The AI learns best from **paired examples**: a PDF and its corresponding LaTeX outline.

### Example Directory Structure

```
examples/
├── example1.pdf              # Your first sample document
├── example1_outline.tex      # The outline you want for this type of document
├── example2.pdf              # Another sample document (different style/topic)
└── example2_outline.tex      # Its corresponding outline
```

### Naming Convention

- PDFs: `example1.pdf`, `example2.pdf`, etc.
- Outlines: `example1_outline.tex` or `example1.tex` (both work)

The script automatically pairs them by matching the base name.

### What the AI Learns

When you provide paired examples, the AI learns:
- **Structure patterns**: How you organize sections and subsections
- **Depth preferences**: Do you use subsubsections? How deep do you go?
- **Style choices**: Formal vs informal section naming
- **Content mapping**: What parts of the PDF become what sections

**Example outline** (`examples/example1_outline.tex`):

```latex
\documentclass{article}
\begin{document}

\section{Introduction}
\subsection{Background}
\subsection{Motivation}

\section{Main Content}
\subsection{Key Concept 1}
\subsection{Key Concept 2}

\section{Conclusion}

\end{document}
```

### Can I Use Only .tex Files?

Yes! If you don't have sample PDFs, you can just provide `.tex` outlines. The AI will still learn the LaTeX structure, but won't understand as well when to apply which patterns. It works, just not as effectively.

**More examples = better results!** Start with 2-3 paired examples for best quality.

## Project Structure

```
pdf-outliner/
├── outline.py              # Main Python script
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Easy Docker setup
├── docker-entrypoint.sh   # Docker startup script
├── examples/              # Your example .tex files
│   ├── example1_outline.tex
│   └── example2_outline.tex
├── input/                 # Place PDFs here
└── output/                # Generated outlines appear here
```

## Available Models

You can use different Ollama models depending on your needs:

- `llama3.2:1b` - Fastest, lowest resource usage (~1GB RAM)
- `llama3.2:3b` - **Recommended** - Good balance (~4GB RAM)
- `llama3.2:7b` - Better quality, slower (~8GB RAM)
- `mistral:7b` - Alternative, good quality (~8GB RAM)

Change the model with the `-m` flag:
```bash
python outline.py input/doc.pdf -m llama3.2:1b
```

## Troubleshooting

### "Ollama connection refused"
Make sure Ollama is running:
```bash
ollama serve
```

### "Model not found"
Pull the model first:
```bash
ollama pull llama3.2:3b
```

### Docker: Model downloads every time
Uncomment the model download line in the Dockerfile to pre-download the model into the image (increases image size by ~2GB).

### Poor outline quality
- Add more example outlines in the `examples/` directory
- Try a larger model (`llama3.2:7b` or `mistral:7b`)
- Ensure your example outlines are consistent in style

## System Requirements

**Python Version:**
- CPU only: 4-8GB RAM (for 3B model)
- GPU (optional): Faster processing

**Docker Version:**
- 8GB+ RAM recommended
- 10GB disk space (for model + container)

## Contributing

Contributions welcome! Feel free to:
- Add support for more document formats
- Improve prompt engineering
- Add more model options
- Improve error handling

## License

MIT License - feel free to use for personal or commercial projects.

## Acknowledgments

- [Ollama](https://ollama.com) - Local AI model runtime
- [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) - PDF text extraction
- Llama models by Meta

---

**Questions?** Open an issue or check the [Ollama documentation](https://github.com/ollama/ollama)