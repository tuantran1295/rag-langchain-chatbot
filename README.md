# RAG Chatbot (React + FastAPI + LangChain)

This is a full-stack Retrieval-Augmented Generation (RAG) application. It allows users to upload PDF documents, processes them into vector embeddings, and enables a chat interface to ask questions about the content of those documents using OpenAI's GPT models.

## Project Architecture

*   **Frontend**: ReactJS (Vite) for the user interface.
*   **Backend**: FastAPI (Python) for the REST API.
*   **RAG Engine**: LangChain for logic, ChromaDB for vector storage, and OpenAI for embeddings/LLM.

## Prerequisites

*   **Node.js** (v16+)
*   **Python** (v3.9+)
*   **OpenAI API Key** (You need credits/access to `gpt-3.5-turbo`).

## Quick Start Guide

This project is divided into two distinct parts: `backend` and `frontend`. You must run both terminals simultaneously.

1.  **Setup Backend**: See [backend/README.md](./backend/README.md).
2.  **Setup Frontend**: See [frontend/README.md](./frontend/README.md).

## Features

*   **PDF Upload**: Uploads are saved locally and processed immediately.
*   **Vector Search**: Uses ChromaDB to find relevant chunks of text.
*   **Contextual Chat**: The LLM answers based *only* on the document context provided.