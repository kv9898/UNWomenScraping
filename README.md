# What is this project for

This is a script I written for my own personal use and I would like to share it on GitHub so it can inspire others.

`crawl.py` downloads the national reports on status of women from the [UN Women website](https://www.unwomen.org/en/how-we-work/commission-on-the-status-of-women/csw69-2025/preparations) to the `downloaded_pdfs` folder.

`PdfSearch.py` searches for specific keywords in the PDFs in the `downloaded_pdfs` folder and saves the results to an Excel file.

`analysis.py` does simple data analysis to get a tally of the countries in the reports.

`trans.py` is a module called by `PdfSearch.py` to translate text from the five non-English languages used in the UN Women reports to English. A number of engines are available and can be selected using the `DEFAULT_ENGINE` variable in the module.