from pymongo import MongoClient
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
MONGO_URI = "mongodb+srv://Dhanaprathan:Dhana%402004@cluster0.z2ttd4o.mongodb.net/?appName=Cluster0"

#MongoDB search Working Module

# --------------------------Peek of stored MongoDB database---------------------
# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["financial_rag_db"]
mongo_collection = db["icici_reports"]
print()

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
# -----------------------searching in MongoDB---------------------------------

print("\n========== 2. RUNNING A MONGODB SEMANTIC SEARCH ==========")
question = "Standalone net cashflow"
print(f"Question: '{question}'")

# Step A: Use Chroma's local model to turn your question into a vector array
default_ef = DefaultEmbeddingFunction()
# .default_ef returns a list of lists, so we grab the first element [0]
question_vector = default_ef([question])[0]

# Convert the question's numpy array vector to a standard Python list of floats
if hasattr(question_vector, "tolist"):
    question_vector = question_vector.tolist()


# Step B: Define the MongoDB Atlas Vector Search Pipeline
# These are the standard fields required for MongoDB ANN search syntax
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",      # Must match the exact name you gave your Atlas index
            "path": "text_embedding",     # The field containing your vectors
            "queryVector": question_vector, # The vector array we generated above
            "numCandidates": 100,         # How many nearby chunks MongoDB evaluates
            "limit": 1                    # Number of top results to return
        }
    }
]

# Step C: Execute search aggregation
results = list(mongo_collection.aggregate(pipeline))

if results:
    best_match = results[0]
    print(f"\n✅ Most relevant answer found on Page {best_match['page_number']}!")
    print("--- Extracted Context ---")
    print(best_match['rag_text'][:500])  # Print first 500 characters
else:
    print("No relevant context found in MongoDB. Check if your Atlas index name matches.")
