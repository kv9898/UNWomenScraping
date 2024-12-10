# What is this project for

This is a script I written for my own personal use and I would like to share it on GitHub so it can inspire others.

`crawl.py` downloads the national reports on status of women from the [UN Women website](https://www.unwomen.org/en/how-we-work/commission-on-the-status-of-women/csw69-2025/preparations) to the `downloaded_pdfs` folder.

`PdfSearch.py` searches for specific keywords in the PDFs in the `downloaded_pdfs` folder and saves the results to an Excel file.

`analysis.py` does simple data analysis to get a tally of the countries in the reports.

`trans.py` is a module called by `PdfSearch.py` to translate text from the five non-English languages used in the UN Women reports to English. A number of engines are available and can be selected using the `DEFAULT_ENGINE` variable in the module.

# Notes
1. The parsing of non-English documents can be disabled by uncommenting lines 56-58 in `PdfSearch.py`.
2. The default translation engine is `google`. But this is subject to usage limits. An alternative is `mymemory`, but it is much slower. `libre` is not usable at the time of writing. Local models are not recommended due to the size of the documents and the complexity involved in running the models with multiprocessing.

# Versions and dependencies
It is recommended that the [UV](https://docs.astral.sh/uv/) project manager is used for this project.

## For UV users

a simple `uv sync` would suffice to replicate the Python environment needed for this project.

## For non-UV users

Python 3.12.8 is used, the versions of the other dependencies are listed in the `requirements.txt` file.