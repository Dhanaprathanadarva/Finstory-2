import fitz
import csv

def extract_all_blocks_to_csv(pdf_path, output_csv_path):
    try:
        doc = fitz.open(pdf_path)
        
        # Open the CSV file for writing
        with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Write the header
            writer.writerow(["Page_Index", "Block_Index", "Content"])
            
            # Loop through every page
            for page_num, page in enumerate(doc):
                # Extract blocks (returns a list of tuples)
                blocks = page.get_text("blocks")
                
                for b in blocks:
                    # b[4] is the text content, b[5] is the block number
                    # We write Page Number, Block ID, and Content
                    writer.writerow([page_num + 1, b[5], b[4].strip()])
        
        doc.close()
        print(f"Successfully extracted all blocks to: {output_csv_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Configuration
pdf_file = r"C:/Users/itinf/Downloads/icici.pdf"
output_file = "extracted_blocks.csv"

# Run the extraction
extract_all_blocks_to_csv(pdf_file, output_file)