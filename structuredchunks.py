import pandas as pd
import pymupdf4llm
import chromadb
from pymongo import MongoClient

def split_page_by_layout(page_chunks):
    """
    Takes your original page_chunks list and splits each page 
    into individual elements: Header/Text chunks and Table chunks.
    """
    advanced_chunks = []

    chunk_counter = 1
    
    for page in page_chunks:
        raw_text = page["text"]
        metadata = page["metadata"]
        
        # ─── THE FIX: Match PyMuPDF4LLM's official keys ───
        page_num = metadata.get("page_number", 1)      # Replaced ["page"]
        source_file = metadata.get("file_path", "unknown") # Replaced ["source"]
        # ──────────────────────────────────────────────────
        
        lines = raw_text.split("\n")
        current_block = []
        is_table = False
        
        
        for line in lines:
            # Check if the line belongs to a markdown table
            is_table_line = "|" in line
            
            # If we switch from text to table, or table to text, save the finished block
            if is_table_line != is_table:
                if current_block:
                    block_text = "\n".join(current_block).strip()
                    if block_text:
                        advanced_chunks.append({
                            "id":chunk_counter,
                            "rag_text": block_text,
                            "page_number": f"Page Number:{page_num}",
                            "source": source_file,
                            "element_type": "table" if is_table else "text"
                        })
                        chunk_counter += 1
                current_block = []
                is_table = is_table_line
            
            current_block.append(line)
            
        # Grab the very last block on the page
        if current_block:
            block_text = "\n".join(current_block).strip()
            if block_text:
                advanced_chunks.append({
                    "id":chunk_counter,
                    "rag_text": block_text,
                    "page": f"Page Number:{page_num}",
                    "source": source_file,
                    "element_type": "table" if is_table else "text"
                })
                chunk_counter+1
                
    return advanced_chunks

# --- How to use it in your code ---
basic_pages = pymupdf4llm.to_markdown(r"C:/Users/itinf/Downloads/SBI.pdf", page_chunks=True)
structured_chunks = split_page_by_layout(basic_pages)
print(len(structured_chunks))
ids = [chunk["id"] for chunk in structured_chunks]
print(ids)