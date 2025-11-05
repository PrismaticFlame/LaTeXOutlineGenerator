#!/usr/bin/env python3
"""
PDF to LaTeX Outline Generator
Extracts text from PDFs and generates LaTeX outlines using a local AI model.
"""

import os
import sys
import argparse
from pathlib import Path
import pymupdf4llm

try:
    import ollama
except:
    print("Error: ollama package not installed")
    print("Install it with: pip install ollama")
    sys.exit(1)

def load_examples(examples_dir: Path) -> str:
    """
    Load paired PDF and LaTeX examples for few-shot learning.
    """
    examples_text = "Here are examples of PDFs and their corresponding LaTeX outlines:\n\n"

    # Find all .tex files
    tex_files = sorted(examples_dir.glob("*.tex"))

    if len(tex_files) == 0:
        print("Warning: No example .tex files found in examples/ directory")
        print("The model will work but may produce less consistent results.")
        return ""
    
    examples_found = 0

    for tex_file in tex_files:
        # Look for corresponding PDF (e.g., example1.pdf for example1_outline.tex)
        # Handle both example1_outline.tex and example1.tex
        base_name = tex_file.stem.replace('_outline', '')
        pdf_file = examples_dir / f"{base_name}.pdf"

        if pdf_file.exists():
            # Extract text from example PDF
            try:
                pdf_text = pymupdf4llm.to_markdown(str(pdf_file))

                # truncate to first ~2000 chars to keep prompt manageable
                pdf_preview = pdf_text[:2000]
                if len(pdf_text) > 2000:
                    pdf_preview += "\n[... content truncated ... ]"

                with open(tex_file, 'r', encoding='utf-8') as f:
                    tex_content = f.read()

                examples_found += 1
                examples_text += f"=== Example {examples_found} ===\n"
                examples_text += f"PDF Content:\n{pdf_preview}\n\n"
                examples_text += f"LaTeX Outline:\n```latex\n{tex_content}\n```\n\n"
 
            except Exception as e:
                print(f"Warning: Could not process example {pdf_file.name}: {e}")

        else:
            # If no PDF found, just show LaTeX structure
            print(f"Note: No PDF found for {tex_file.name} (looking for {pdf_file.name})")
            print(f"    You can still use it, but the model learns better with paired examples.")

            with open(tex_file, 'r', encoding='utf-8') as f:
                tex_content = f.read()

            examples_found += 1
            examples_text += f"=== Example {examples_found} (LaTeX structure only) ===\n"
            examples_text += f"LaTeX Outline:\n```latex{tex_content}\n```\n\n"

    if examples_found > 0:
        print(f"Loaded {examples_found} example(s)")
    
    return examples_text


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract text from PDF using pymupdf4llm
    """
    try:
        # Extract as markdown for better structure preservation
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        return md_text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        sys.exit(1)


def generate_outline(pdf_text: str, examples: str, model: str = "llama3.2:3b") -> str:
    """
    Generate LaTeX outline using Ollama.
    """

    # Truncate PDF text if too long (keep first ~6000 characters for context)
    if len(pdf_text) > 6000:
        pdf_text_preview = pdf_text[:6000] + "\n\n[... document continues ...]"
    else:
        pdf_text_preview = pdf_text
    
    prompt = f"""{examples}

    Now, based on the examples above, create a LaTeX outline for the following NEW document.
    Follow the EXACT style you see in the examples:
    - ONLY use \\section{{}} and \\subsection{{}} commands
    - DO NOT include any code blocks, figures, tables, or content
    - DO NOT include \\begin{{verbatim}}, \\begin{{figure}}, or \\begin{{table}}
    - Match the document structure and preamble style from the examples
    - An outline is just the hierarchical structure of sections, nothing more

    New Document Content:
    {pdf_text_preview}

    Generate the LaTeX outline:"""

    try:
        print(f"    Calling ollama.chat with model={model}...")
        response = ollama.chat(
            model,
            messages=[
                {
                    'role': 'system',
                    'content': '''You are a helpful assistant the creates well-structured LaTeX document outlines. You only output valid LaTeX code with no explanations or markdown formatting.
                    An outline contains ONLY the document structure: sections and subsections with titles.
                    DO NOT include:
                    - Code blocks or verbatim text
                    - Figures, tables, or captions
                    - Actual content or explanations
                    - Any text besides section/subsection commands
                    Only output valid LaTeX outline code with \section{} and \subsection{} commands.'''
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        return response['message']['content']
    
    except Exception as e:
        print(f"Error generating outline: {e}")
        print("\nMake sure Ollama is running and the model is installed:")
        print(f"  ollama pull {model}")
        sys.exit(1)


def save_outline(outline: str, output_path: Path):
    """
    Save the generated outline to a file.
    """
    # Clean up the output - remove markdown code blocks if present
    outline = outline.strip()
    if outline.startswith("```latex"):
        outline = outline[8:]
    if outline.startswith("```"):
        outline = outline[3:]
    if outline.endswith("```"):
        outline = outline[:-3]
    outline = outline.strip()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(outline)

    print(f"outline saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate LaTeX outlines from PDF documents using AI",
        epilog="""
Examples:
  python outline.py input/mydoc.pdf
  python outline.py input/mydoc.pdf -o custom_outline.tex
  python outline.py input/mydoc.pdf -m llama3.2:1b
        """
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the PDF file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output path for LaTeX file (default: output/<pdf_name>_outline.tex)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="llama3.2:3b",
        help="Ollama model to use (default: llama3.2:3b)"
    )
    parser.add_argument(
        "-e", "--examples",
        type=str,
        default="examples",
        help="Directory containing example PDFs and .tex files (default: examples/)"
    )

    args = parser.parse_args()

    # Setup paths
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path("output") / f"{pdf_path.stem}_outline.tex"
    
    examples_dir = Path(args.examples)
    
    print(f"📄 Processing: {pdf_path.name}")
    print(f"🤖 Using model: {args.model}")
    
    # Load examples
    print("📚 Loading examples...")
    examples = load_examples(examples_dir)
    
    # Extract PDF text
    print("🔍 Extracting text from PDF...")
    pdf_text = extract_pdf_text(pdf_path)
    print(f"   Extracted {len(pdf_text)} characters")
    
    # Generate outline
    print("✨ Generating outline (this may take 10-30 seconds)...")
    outline = generate_outline(pdf_text, examples, args.model)
    
    # Save output
    save_outline(outline, output_path)
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
