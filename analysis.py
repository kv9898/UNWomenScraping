import polars as pl
import re

kwic = pl.read_excel("kwic_results.xlsx")


# create a summary of the countries
def extract_country(pdf_name) -> str:
    match = re.search(r"b\d+_[^_]+_([^_]+(?:_[^_]+)*)_[a-z]{2}(?:_\d+)?\.pdf$", pdf_name)
    # match = re.search(r"b30_[^_]+_([^_]+)_[a-z]{2}(?:_\d+)?\.pdf$", pdf_name)
    if match:
        return match.group(1)  # The country name is in the first capture group
    return None

kwicSum = kwic.with_columns(
    pl.col("Document").map_elements(extract_country, return_dtype=pl.String).alias("country")
).group_by("country").agg(
    [
        pl.len().alias("count")
    ]
).sort("count", descending=True)
