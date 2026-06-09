import fitz
import csv
import pandas as pd
import pymupdf4llm
import pymupdf



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

