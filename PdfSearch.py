import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from PyPDF2 import PdfReader
from googletrans import Translator
import re
import polars as pl
import json

# Keywords to search for
KEYWORDS = ["fertility", "economic participation", "labour participation", "labor participation"]

pdf_folder = "downloaded_pdfs"  # Folder containing the PDFs
output_file = "kwic_results.xlsx"  # Output Excel file

# Progress file to keep track of processed PDFs
PROGRESS_FILE = "progress.json"

# Initialize translator
translator = Translator()

# Load progress
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"processed_files": []}

# Save progress
def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=4)

# Function to process a single PDF
def process_pdf(pdf_path):
    results = []

    try:
        # Read the PDF
        reader = PdfReader(pdf_path)
        pdf_name = os.path.basename(pdf_path)

        match = re.search(r'_([a-z]{2})(?:_\d+)?\.pdf$', pdf_name)
        if not match:
            print(f"Could not extract language from {pdf_name}, skipping.")
            return results
        detected_language = match.group(1)

        # Validate the detected language
        if detected_language not in ["en", "fr", "es", "ar", "ru", "zh"]:
            print(f"Suspicious Unsupported language {detected_language} in {pdf_name}, check out later.")

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text.strip():
                continue  # Skip empty pages

            try:
                if detected_language != "en":
                    detected_language = "zh-CN"if detected_language == "zh" else detected_language
                    translated_text = translator.translate(text, src=detected_language, dest="en").text
                else:
                    translated_text = text
            except Exception as e:
                print(f"Translation failed for {pdf_name}, page {page_number}: {e}")
                translated_text = ""

            # Search for keywords in the translated text
            for keyword in KEYWORDS:
                if keyword.lower() in translated_text.lower():
                    # Capture the surrounding context
                    keyword_index = translated_text.lower().find(keyword.lower())
                    start_index = max(0, keyword_index - 50)
                    end_index = min(len(translated_text), keyword_index + 50)
                    context = translated_text[start_index:end_index]

                    # Save the result
                    results.append({
                        "Document": pdf_name,
                        "Page": page_number,
                        "Keyword": keyword,
                        "Context (Translated)": context,
                        "Context (Original)": text[start_index:end_index],
                        "Language": detected_language
                    })
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None

    print(f"Processed {pdf_name}")
    return results

# Function to process all PDFs
def process_all_pdfs(pdf_folder, output_file, num_workers=4):
    # Get all PDF files in the folder
    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    # Load progress
    progress = load_progress()
    processed_files = set(progress["processed_files"])
    remaining_files = [f for f in pdf_files if os.path.basename(f) not in processed_files]

    try:
        # Use multiprocessing for faster processing
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(process_pdf, pdf_path): pdf_path for pdf_path in remaining_files}
            for future in as_completed(futures):
                pdf_path = futures[future]
                try:
                    pdf_results = future.result()

                    if pdf_results is not None:  # Skip if None
                        if pdf_results:  # Process non-empty results
                            # Read the existing Excel file safely
                            existing_df = safe_read_excel(output_file)
                            new_df = pl.DataFrame(pdf_results)

                            # Append new results
                            combined_df = pl.concat([existing_df, new_df], how="vertical").unique()

                            # Write back to the Excel file
                            combined_df.write_excel(output_file)

                        # Mark the file as processed regardless of results
                        processed_files.add(os.path.basename(pdf_path))
                        progress["processed_files"] = list(processed_files)
                        save_progress(progress)

                except Exception as e:
                    print(f"Error processing {pdf_path}: {e}")

        print(f"Results saved to {output_file}")
    except KeyboardInterrupt:
        print("\nInterrupted! Saving progress...")
        save_progress(progress)
        print("Progress saved. You can resume the process later.")
        exit()

def safe_read_excel(file_path):
    """
    Safely read an Excel file using Polars.
    If the file is corrupt or unreadable, return an empty DataFrame.
    """
    try:
        return pl.read_excel(file_path, raise_if_empty=False)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        print("Creating a new file instead.")
        return pl.DataFrame([])

# Main function
def main():
    # Process all PDFs
    process_all_pdfs(pdf_folder, output_file, num_workers=4)

if __name__ == "__main__":
    main()
