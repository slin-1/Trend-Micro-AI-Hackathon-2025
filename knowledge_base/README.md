# Knowledge Base for Linux to Windows Code Conversion

## Overview
This directory contains the knowledge base for the AI Employee workflow system, specifically focused on Linux to Windows code conversion patterns.

## Structure
- `pdfs/` - PDF documents containing Linux to Windows conversion guides, API documentation, and best practices
- `processed/` - Processed and indexed knowledge base entries (auto-generated)

## Usage
1. Add PDF files to the `pdfs/` folder containing:
   - Linux to Windows API conversion guides
   - C/C++ code conversion patterns  
   - Windows-specific implementation examples
   - Best practices for cross-platform development

2. The RAG system will automatically process these PDFs and create embeddings for retrieval

## Supported File Types
- PDF documents (.pdf)
- Text files (.txt, .md)
- Code documentation

## Notes
- The system uses ChromaDB for vector storage
- Embeddings are generated using Trend Micro's text-embedding-3-large model
- Knowledge base is automatically updated when new files are added