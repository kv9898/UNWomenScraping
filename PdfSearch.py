import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
# from PyPDF2 import PdfReader
from pypdf import PdfReader
from trans import trans
import re
import polars as pl
import json
import signal

# Keywords to search for
KEYWORDS = ["fertility", "economic participation", "labour participation", "labor participation"]

pdf_folder = "downloaded_pdfs"  # Folder containing the PDFs
output_file = "kwic_results.xlsx"  # Output Excel file
PROGRESS_FILE = "progress.json"  # Progress file to keep track of processed PDFs

STOP_SIGNAL = False  # Global variable to track Ctrl+C

# Signal handler for Ctrl+C
def signal_handler(signal, frame):
    global STOP_SIGNAL
    print("\nCtrl+C detected. Saving progress and exiting...")
    STOP_SIGNAL = True  # Notify the script to stop gracefully

# Attach signal handler
signal.signal(signal.SIGINT, signal_handler)

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

# Process a single PDF
def process_pdf(pdf_path):
    results = []
    try:
        reader = PdfReader(pdf_path)
        pdf_name = os.path.basename(pdf_path)

        # Detect language from file name
        match = re.search(r'_([a-z]{2})(?:_\d+)?\.pdf$', pdf_name)
        if not match:
            print(f"Could not extract language from {pdf_name}, skipping.")
            return None
        detected_language = match.group(1)

        # uncomment to disable non-english translation
        # if detected_language != "en":
        #     print(f"Skipping {pdf_name} due to non-English language ({detected_language})")
        #     return None

        for page_number, page in enumerate(reader.pages, start=1):
            if STOP_SIGNAL:  # Check for termination request
                return results

            try:
                text = page.extract_text()
                if not text.strip():
                    continue  # Skip empty or invalid pages
            except Exception as e:
                print(f"Failed to extract text from {pdf_name}, page {page_number}: {e}")
                continue

            try:
                if detected_language != "en":
                    # detected_language = "zh-CN" if detected_language == "zh" else detected_language
                    translated_text = trans(text, detected_language)
                else:
                    translated_text = text
            except Exception as e:
                print(f"Translation failed for {pdf_name}, page {page_number}: {e}")
                continue

            for keyword in KEYWORDS:
                if keyword.lower() in translated_text.lower():
                    keyword_index = translated_text.lower().find(keyword.lower())
                    start_index = max(0, keyword_index - 50)
                    end_index = min(len(translated_text), keyword_index + 50)
                    context = translated_text[start_index:end_index]

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
    print(f"Processed {pdf_name}")
    return results

# Process all PDFs
def process_all_pdfs(pdf_folder, output_file, num_workers=4):
    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    progress = load_progress()
    processed_files = set(progress["processed_files"])
    remaining_files = [f for f in pdf_files if os.path.basename(f) not in processed_files]

    try:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(process_pdf, pdf_path): pdf_path for pdf_path in remaining_files}
            for future in as_completed(futures):
                if STOP_SIGNAL:  # Terminate gracefully if Ctrl+C is detected
                    print("\nTerminating workers...")
                    for f in futures:
                        f.cancel()  # Cancel remaining tasks
                    break

                pdf_path = futures[future]
                pdf_name = os.path.basename(pdf_path)

                try:
                    pdf_results = future.result()

                    if pdf_results is not None:  # Skip if None
                        if pdf_results:  # Process non-empty results
                            existing_df = safe_read_excel(output_file)
                            new_df = pl.DataFrame(pdf_results)
                            combined_df = pl.concat([existing_df, new_df], how="vertical").unique()
                            combined_df.write_excel(output_file)

                        # Mark file as processed and save progress
                        processed_files.add(pdf_name)
                    progress["processed_files"] = list(processed_files)
                    save_progress(progress)

                except Exception as e:
                    print(f"Error processing {pdf_path}: {e}")

    except KeyboardInterrupt:
        print("\nCtrl+C detected. Saving progress...")
        progress["processed_files"] = list(processed_files)
        save_progress(progress)
        sys.exit(0)

    print(f"Results saved to {output_file}")

# Safely read Excel file
def safe_read_excel(file_path):
    try:
        return pl.read_excel(file_path, raise_if_empty=False)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        print("Creating a new file instead.")
        return pl.DataFrame([])

# Main function
def main():
    process_all_pdfs(pdf_folder, output_file, num_workers=4)

if __name__ == "__main__":
    main()