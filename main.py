import fitz  # PyMuPDF

def extract_text_to_file(pdf_path, output_txt_path):
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        print(len(doc))

        page = doc[0]

# Extract using "blocks" to see how it groups the text
        blocks = page.get_text("blocks")
        print(len(blocks))

        # for b in blocks:
        #     print(f"Block No: {b[5]}") # The box around the text
        #     print(f"Content: {b[4]}")      # The actual text inside
        #     print("-" * 20)

        print(f"Contents:{blocks[16][4]}")
        
        # Open (or create) the text file for writing
        # with open(output_txt_path, "w", encoding="utf-8") as f:
        #     for page in doc:
        #         text = page.get_text()
        #         f.write(text)
        #         f.write("\n--- End of Page ---\n\n")
        
        # doc.close()
        # print(f"Successfully extracted text to: {output_txt_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Configuration
pdf_file = r"C:/Users/itinf/Downloads/icici.pdf"
output_file = "extracted_data1.txt"

# Run the extraction
extract_text_to_file(pdf_file, output_file)