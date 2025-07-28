from utils import process_collection
import os
import json

collections_dir = "collections"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


for collection in os.listdir(collections_dir):
    collection_path = os.path.join(collections_dir, collection)
    if not os.path.isdir(collection_path):
        continue
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    output_json_path = os.path.join(output_dir, f"{collection}_output.json")
    pdf_dir = os.path.join(collection_path, "PDFs")

    print(f"Processing: {collection}")
    with open(input_json_path) as f:
        input_config = json.load(f)

    result = process_collection(input_config, pdf_dir)

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"Output saved: {output_json_path}")

print("\nAll collections processed!!")
