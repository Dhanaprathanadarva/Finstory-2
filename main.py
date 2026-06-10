import fitz
import csv
import pandas as pd
import pymupdf4llm
import pymupdf
import chromadb
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://Dhanaprathan:Dhana%402004@cluster0.z2ttd4o.mongodb.net/?appName=Cluster0"



# -------------------------------------------------------------------------------------------
# def extract_all_blocks_to_csv(pdf_path, output_csv_path):
#     try:
#         doc = fitz.open(pdf_path)
        
#         # Open the CSV file for writing
#         with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
#             writer = csv.writer(f)
#             # Write the header
#             writer.writerow(["Page_Index", "Block_Index", "Content"])
            
#             # Loop through every page
#             for page_num, page in enumerate(doc):
#                 # Extract blocks (returns a list of tuples)
#                 blocks = page.get_text("blocks")
                
#                 for b in blocks:
#                     # b[4] is the text content, b[5] is the block number
#                     # We write Page Number, Block ID, and Content
#                     writer.writerow([page_num + 1, b[5], b[4].strip()])
        
#         doc.close()
#         print(f"Successfully extracted all blocks to: {output_csv_path}")
        
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Configuration
# pdf_file = r"C:/Users/itinf/Downloads/icici.pdf"
# output_file = "extracted_blocks.csv"

# # Run the extraction
# extract_all_blocks_to_csv(pdf_file, output_file)

# -------------------------------------------------------------------------------------------------

#--------------------------------- For RAG Pipeline Extracting as tables---------------------------

# def extract_dynamic_tables_for_rag(pdf_path):
#     all_rag_context = []
#     doc = fitz.open(pdf_path)
    
#     for page_num, page in enumerate(doc):
#         tabs = page.find_tables(strategy="text")
        
#         for tab in tabs:
#             df = tab.to_pandas()
            
#             # Dynamically convert each row to a string
#             for _, row in df.iterrows():
#                 # Get column names (headers) and their values
#                 details = []
#                 for col_name, value in row.items():
#                     # Only add if the value is not empty/null
#                     if pd.notna(value) and str(value).strip():
#                         details.append(f"{col_name}: {value}")
                
#                 # Combine into a single descriptive sentence
#                 sentence = "Transaction details: " + ", ".join(details) + "."
                
#                 all_rag_context.append({
#                     "page": page_num + 1,
#                     "rag_text": sentence
#                 })
    
#     doc.close()
#     return all_rag_context

# # Usage
# data = extract_dynamic_tables_for_rag(r"C:/Users/itinf/Downloads/icici.pdf")
# for item in data[:3]:
#     print(item['rag_text'])


# --------------------------------------------------------------------------------------------

def extract_pdf_for_rag(pdf_path):
    print(f"Processing {pdf_path} for RAG...")
    
    # The magic parameter: page_chunks=True
    # This automatically splits the extraction page-by-page and preserves tables as Markdown
    page_chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    print(page_chunks[15]["metadata"])
    
    all_rag_context = []
    
    for chunk in page_chunks:
        # chunk["metadata"]["page"] is 0-indexed, so we add 1
        page_num = chunk["metadata"]["page_number"]
        
        # chunk["text"] contains the clean text AND perfectly formatted Markdown tables
        md_text = chunk["text"]
        
        # Only add pages that actually have content
        if md_text.strip():
            all_rag_context.append({
                "page": page_num,
                "rag_text": md_text
            })
            
    print(f"Successfully extracted {len(all_rag_context)} pages of RAG-ready context.")
    return all_rag_context


pdf_file = r"C:/Users/itinf/Downloads/icici.pdf"
    
rag_data = extract_pdf_for_rag(pdf_file)
    
    # Print the exact context you will send to your Vector Database / Embeddings model
    # Let's look at the first page as an example
# if rag_data:
#     print(f"\n--- Preview of Page {rag_data[0]['page']} ---")
#     print(rag_data[0]['rag_text'][:1000]) # Printing first 1000 characters

# -----------------Extraction complete-----------------------------------------------------

# ------------------------------------Vector Database in ChromaDB-----------------------------

def embed_and_store_data(rag_data):
    print("Initializing Vector Database...")
    
    # 1. Create a local Vector Database instance
    # This will create a folder called "my_vectordb" in your project directory
    chroma_client = chromadb.PersistentClient(path="./my_vectordb")
    
    # 2. Create a "collection" (think of this like a table in an SQL database)
    # By default, Chroma automatically uses the 'all-MiniLM-L6-v2' embedding model!
    collection = chroma_client.get_or_create_collection(name="icici_financial_statements")
    
    # 3. Prepare our data lists for Chroma
    documents = []
    metadatas = []
    ids = []
    
    for chunk in rag_data:
        # The Markdown text (including the tables)
        documents.append(chunk["rag_text"])
        
        # The metadata so we know exactly where the answer came from
        metadatas.append({"page_number": chunk["page"]})
        
        # A unique ID for each chunk
        ids.append(f"page_{chunk['page']}")
        
    print(f"Embedding {len(documents)} pages... (This might take a moment the first time)")
    
    # 4. Add to the database! 
    # Chroma automatically converts your Markdown strings into vector embeddings here.
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print("Successfully embedded and stored all data!")
    return collection

# --- Usage ---
# Assuming 'rag_data' is the list you extracted from pymupdf4llm
my_collection = embed_and_store_data(rag_data)


# ---------------------------------Vector embeddings and search sample(chromaDB)------------------------------

# --- 1. Peek at the raw data and the Vector ---
print("\n========== 1. PEEKING INSIDE THE DATABASE ==========")
# .peek(1) grabs exactly 1 chunk from the database so we can inspect it
peek_data = my_collection.peek(1)

print(f"Chunk ID: {peek_data['ids'][0]}")
print(f"Metadata: {peek_data['metadatas'][0]}")
print(f"Text Snippet: {peek_data['documents'][0][:150]}...") # Printing first 150 chars

# Let's look at the actual mathematical vector!
vector = peek_data['embeddings'][0]
print(f"\nVector Dimensions (Length): {len(vector)} numbers")
print(f"First 5 numbers of the embedding: {vector[:5]}")


# --- 2. Run your first Semantic Search! ---
print("\n========== 2. RUNNING A SEMANTIC SEARCH ==========")
question = "Standalone net cashflow"
print(f"Question: '{question}'")

# .query() automatically embeds your question and searches the database
results = my_collection.query(
    query_texts=[question],
    n_results=1 # We only want the top 1 most relevant page
)

# Extracting the results
best_page = results['metadatas'][0][0]['page_number']
best_text = results['documents'][0][0]

print(f"\n✅ Most relevant answer found on Page {best_page}!")
print("--- Extracted Context ---")
print(best_text[:500]) # Printing the first 500 characters of the best match

# ------------------------------------------------chroma DB to MONGODB---------------------------------

def push_chroma_to_mongodb(chroma_collection):
    print("1. Extracting data & vectors from Chroma...")
    chroma_data = chroma_collection.get(
        include=['embeddings', 'documents', 'metadatas']
    )
    
    # Setup MongoDB Connection (using your local default port)
    
    print("2. Connecting to MongoDB Backend...")
    mongo_client = MongoClient(MONGO_URI)
    
    db = mongo_client["financial_rag_db"]
    mongo_collection = db["icici_reports"]
    
    print("3. Restructuring data for MongoDB JSON format...")
    mongo_documents = []
    
    for i in range(len(chroma_data['ids'])):
        # --- THE CRITICAL FIX ---
        # Get the embedding array
        embedding_data = chroma_data['embeddings'][i]
        
        # If it's a numpy array, convert it to a native Python list of floats
        if hasattr(embedding_data, "tolist"):
            embedding_data = embedding_data.tolist()
        # ------------------------

        doc = {
            "_id": chroma_data['ids'][i],                      
            "rag_text": chroma_data['documents'][i],           
            "page_number": chroma_data['metadatas'][i]['page_number'], 
            "text_embedding": embedding_data     # <--- Now a clean Python list!
        }
        mongo_documents.append(doc)
        
    if mongo_documents:
        print(f"4. Pushing {len(mongo_documents)} chunks with embeddings to MongoDB...")
        mongo_collection.delete_many({}) 
        
        mongo_collection.insert_many(mongo_documents)
        print("🚀 Success! Your vectors and markdown text are safely stored in MongoDB.")
    else:
        print("❌ No data found inside the Chroma collection.")

# --- How to invoke it ---
# Pass your active 'my_collection' variable directly into the function
push_chroma_to_mongodb(my_collection)

# ----------------------------------------MONGODB Searching and peeking----------------------------
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["financial_rag_db"]
mongo_collection = db["icici_reports"]

print("\n========== 1. PEEKING INSIDE MONGODB ==========")
# Grab exactly 1 document from the collection
peek_data = mongo_collection.find_one()

if peek_data:
    print(f"Document ID: {peek_data['_id']}")
    print(f"Page Number: {peek_data['page_number']}")
    print(f"Text Snippet: {peek_data['rag_text'][:150]}...")
    
    # Extract the actual mathematical vector array
    vector = peek_data['text_embedding']
    print(f"\nVector Dimensions (Length): {len(vector)} numbers")
    print(f"First 5 numbers of the embedding: {vector[:5]}")
else:
    print("Database is empty!")