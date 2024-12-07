import PyPDF2
import re

# open the pdf file
reader = PyPDF2.PdfReader("beijing30_guidance_note_zhs.pdf")

# get number of pages
num_pages = len(reader.pages)

# define key terms
string = "生育"

# extract text and do the search
pageNum = 0
for page in reader.pages:
    pageNum += 1
    text = page.extract_text()
    # print(text)
    res_search = re.search(string, text)
    print(f"page: {pageNum}, res_search: {res_search}") 
