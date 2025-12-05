# RAG Chatbot Backend

The backend is built with **FastAPI**. It handles file uploads, processes PDFs using **LangChain**, creates embeddings, and stores them in **ChromaDB**.

## Requirements

*   Python 3.9 or higher
*   An OpenAI API Key

## Installation

1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```

2.  Create a virtual environment (recommended):
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Open the `.env` file and add your API key:
    ```env
    OPENAI_API_KEY=sk-your-actual-api-key-here
    ```

## Running the Server

Start the FastAPI server:

```bash
python main.py