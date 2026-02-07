import os
import PyPDF2
import pdfplumber
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import re

load_dotenv()

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using pdfplumber for better accuracy
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error extracting text with pdfplumber: {e}")
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e2:
            print(f"Error extracting text with PyPDF2: {e2}")
    
    return text

def clean_text(text):
    """
    Clean extracted text by removing extra whitespaces and fixing common OCR issues
    """
    # Remove extra whitespaces and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers and headers/footers that might have been captured
    text = re.sub(r'\d+\s*\n\s*', '', text)
    # Remove multiple consecutive spaces
    text = re.sub(r'[ \t]{2,}', ' ', text)
    # Fix common OCR issues
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    return text.strip()

def process_cpcb_documents(pdf_directory="./data/cpcb_pdfs/", chunk_size=1000, chunk_overlap=100):
    """
    Process CPCB documents: PDF extraction → text cleaning → chunking → embedding → Pinecone upsert
    """
    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    
    # Create or connect to index
    index_name = os.getenv("PINECONE_INDEX_NAME", "cpcb-waste-rules")
    
    # Check if index exists, if not create it
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric='cosine'
        )
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    # Process all PDFs in the directory
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    all_chunks = []
    metadatas = []
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        print(f"Processing {pdf_file}...")
        
        # Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text:
            print(f"No text extracted from {pdf_file}")
            continue
        
        # Clean the text
        cleaned_text = clean_text(raw_text)
        
        # Split text into chunks
        chunks = text_splitter.split_text(cleaned_text)
        
        # Prepare metadata for each chunk
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            metadatas.append({
                "source": pdf_file,
                "chunk_id": i,
                "page_content_length": len(chunk),
                "material_type": "general",  # Will be updated based on content analysis
                "compliance_type": "cpcb_2016"
            })
    
    if all_chunks:
        # Create Pinecone vectorstore
        vectorstore = Pinecone.from_texts(
            texts=all_chunks,
            embedding=embeddings,
            index_name=index_name,
            metadatas=metadatas
        )
        
        print(f"Ingested {len(all_chunks)} text chunks into Pinecone index '{index_name}'")
        return vectorstore
    else:
        print("No chunks to ingest")
        return None

def test_ingestion():
    """
    Test function to verify ingestion works correctly
    """
    # Create a sample text if no PDFs are available
    sample_cpcb_rules = """
    CENTRAL POLLUTION CONTROL BOARD
    GUIDELINES FOR WASTE MANAGEMENT
    
    Chapter 1: General Provisions
    1.1 These guidelines shall be called the Solid Waste Management Rules.
    1.2 These shall come into force on the date of their publication in the Official Gazette.
    
    Chapter 2: Definitions
    2.1 "Biodegradable waste" means any organic matter in waste which can be broken down into simpler substances by microorganisms.
    2.2 "Construction and demolition waste" means waste generated during construction, renovation, repair and demolition activities.
    
    Chapter 3: Segregation of Waste
    3.1 Waste generators shall segregate waste into biodegradable, non-biodegradable and domestic hazardous waste.
    3.2 Segregation shall be done at source by the waste generator.
    
    Chapter 4: Prohibition of Disposal
    4.1 No person shall discharge untreated waste into water bodies.
    4.2 No person shall dispose of hazardous waste without authorization.
    
    Schedule I: Hazardous Materials
    - Batteries containing lead, mercury, cadmium
    - Pesticides and insecticides
    - Medical waste from healthcare facilities
    - Electronic waste (computers, mobile phones, etc.)
    
    Schedule II: Plastic Waste Management
    - Manufacturers and producers responsible for collection and recycling
    - Extended Producer Responsibility (EPR) implementation
    - Minimum thickness requirements for carry bags
    """
    
    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )
    
    # Create or connect to index
    index_name = os.getenv("PINECONE_INDEX_NAME", "cpcb-waste-rules")
    
    # Check if index exists, if not create it
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            dimension=1536,  # OpenAI embedding dimension
            metric='cosine'
        )
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Split sample text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    
    chunks = text_splitter.split_text(sample_cpcb_rules)
    
    # Prepare metadata
    metadatas = []
    for i, chunk in enumerate(chunks):
        metadatas.append({
            "source": "sample_cpcb_guidelines",
            "chunk_id": i,
            "page_content_length": len(chunk),
            "material_type": "general",
            "compliance_type": "cpcb_2016"
        })
    
    # Create Pinecone vectorstore
    vectorstore = Pinecone.from_texts(
        texts=chunks,
        embedding=embeddings,
        index_name=index_name,
        metadatas=metadatas
    )
    
    print(f"Created sample index with {len(chunks)} chunks")
    return vectorstore

if __name__ == "__main__":
    # For testing purposes, create a sample directory if it doesn't exist
    os.makedirs("./data/cpcb_pdfs/", exist_ok=True)
    
    # Run the test ingestion
    test_ingestion()
    print("Sample CPCB rules ingested successfully!")