import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain


load_dotenv()

# Directory to save the FAISS index
PERSIST_DIRECTORY = "./faiss_db"

def process_document(file_path):
    # 1. Load PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    # 3. Create Embeddings
    embedding_function = OpenAIEmbeddings()

    # 4. Store in FAISS and save locally
    vectorstore = FAISS.from_documents(splits, embedding_function)
    vectorstore.save_local(PERSIST_DIRECTORY)

    return "Document processed and stored successfully."

def query_rag(query_text):
    # 1. Load Database
    embedding_function = OpenAIEmbeddings()

    # Load FAISS
    vectorstore = FAISS.load_local(
        PERSIST_DIRECTORY,
        embedding_function,
        allow_dangerous_deserialization=True
    )

    # 2. Create Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 3. Create LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # 4. Create Prompt (Required for new chains)
    # This tells the LLM how to use the context
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {input}
    """)

    # 5. Create the Chain (Modern replacement for RetrievalQA)
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # 6. Run Query
    # Note: The input key is usually "input" in these new chains
    response = retrieval_chain.invoke({"input": query_text})

    # The answer is in the "answer" key, context is in "context"
    return response["answer"]