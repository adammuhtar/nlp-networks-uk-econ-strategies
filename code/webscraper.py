"""
Python script to web scrape government policy paper documents from GOV.UK
@author: Adam Muhtar
"""

# Import libraries
from bs4 import BeautifulSoup
import os
import pandas as pd
import pdfplumber
import pypandoc
import re
import requests
import string
import unicodedata
from urllib.request import Request, urlopen

# Create a new directory "speeches"
doc_dir = "../texts"    # file path should be changed accordingly

# List of GOV.UK policy papers queried search pages
# Check search listing at https://www.gov.uk/search/policy-papers-and-consultations and update page range
URL_PART_1 = "https://www.gov.uk/search/policy-papers-and-consultations?content_store_document_type%5B%5D=policy_papers&order=updated-oldest&page="
URL_PART_2 = "&public_timestamp%5Bfrom%5D=3%2F3%2F2021"
search_urls = [URL_PART_1 + str(x) + URL_PART_2 for x in range(1, 109)]

# Extracting URLs from GOV.UK policy papers search pages
paths = []
for url in search_urls:
    soup = BeautifulSoup(urlopen(Request(url)), "lxml")
    for path in soup.findAll("a"):
        paths.append(path.get("href"))
paths = [path for path in paths if "/government/publications/" in path]
paths = [path for path in paths if "/build-back-better-our-plan-for-growth" not in path and "/uk-innovation-strategy-leading-the-future-by-creating-it" not in path]

# Removing duplicate paths from GOV.UK policy papers search pages URL extraction
paths_check = paths.copy()
paths_duplicate = []
for path in paths:
    for i in range(0, len(paths_check)):
        if path + "/" in paths_check[i]:
            paths_duplicate.append(paths_check[i])
paths_clean = [path for path in paths if path not in paths_duplicate]
doc_urls = ["https://www.gov.uk" + path for path in paths_clean]

# Web scraping policy paper document URL from home pages
doc_paths = []
doc_org = []
for url in doc_urls:
    temp_href = []
    temp_path = []
    temp_org = []
    # HTML parser using BeautifulSoup
    soup = BeautifulSoup(urlopen(Request(url)), "lxml")
    for path in soup.findAll("a"):
        temp_href.append(path.get("href"))
    # Select the first instance of HTML/PDF href attribute
    for i in range(0, len(temp_href)):
        if url == "https://www.gov.uk/government/publications/levelling-up-the-united-kingdom":
            temp_path.append(
                "https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1054769/Levelling_Up_the_United_Kingdom__accessible_version_.pdf"
            )
            break
        elif url == "https://www.gov.uk/government/publications/declaration-on-government-reform":
            temp_path.append(
                "/government/publications/declaration-on-government-reform/declaration-on-government-reform"
            )
            break
        elif any(
            x in temp_href[i] for x in [
                "/government/publications/",
                "https://assets.publishing.service.gov.uk/"
            ]
        ):
            temp_path.append(temp_href[i])
            break
    # Append HTML directories with GOV.UK URL; append to doc_paths
    if temp_path != []:
        if "/government/publications/" in temp_path[0]:
            temp_path[0] = "https://www.gov.uk" + temp_path[0]
            doc_paths.append(temp_path[0])
            # Select the first instance of organisation href attribute
            for i in range(0, len(temp_href)):
                if any(x in temp_href[i] for x in ["/government/organisations/"]):
                    temp_org.append(temp_href[i])
                    break
            if temp_org != []:
                temp_org[0] = temp_org[0].replace("/government/organisations/", "")
                doc_org.append(temp_org[0])
            else:
                pass
        else:
            doc_paths.append(temp_path[0])
            # Select the first instance of organisation href attribute
            for i in range(0, len(temp_href)):
                if any(x in temp_href[i] for x in ["/government/organisations/"]):
                    temp_org.append(temp_href[i])
                    break
            if temp_org != []:
                temp_org[0] = temp_org[0].replace("/government/organisations/", "")
                doc_org.append(temp_org[0])
            else:
                pass
    else:
        pass

# Zip URL and organisation lists into pandas dataframe
doc_df = pd.DataFrame(list(zip(doc_paths, doc_org)), columns = ["url", "org"])

# Create list of HTML document URLs
html_urls = []
html_texts = []
for url in doc_paths:
    if "https://www.gov.uk/government/publications/" in url:
        html_urls.append(url)
for i in range(0, len(html_urls)):
    if "https://www.gov.ukhttps://www.gov.uk/government/publications/" in html_urls[i]:
        html_urls[i] = re.sub(r".", "", html_urls[i], count = 18)

# Text extraction of HTML documents
for url in html_urls:
    temp_text = ""
    html = urlopen(url).read()
    html_parsed = BeautifulSoup(html, features = "html.parser")
    for text in html_parsed.find_all("h2"):
        temp_text += text.get_text()
    for text in html_parsed.find_all("p"):
        temp_text += text.get_text()
    # translating unicode strings into normal characters
    temp_text = unicodedata.normalize("NFKD", temp_text)
    # convert string to lowercases
    temp_text = temp_text.lower()
    # remove all punctuation symbols, except for "&()-."
    temp_text = temp_text.translate(
        str.maketrans(
            "",
            "",
            string.punctuation[:5]
            + string.punctuation[6]
            + string.punctuation[9:12]
            + string.punctuation[14:],
        )
    )
    # replace newline character with white space
    temp_text = temp_text.replace("\n", " ")
    # remove excess whitespaces
    temp_text = re.sub(" +", " ", temp_text)
    html_texts.append(temp_text)

# PDF scrapping from policy paper URLs
# Download all files from URLs starting with "https://assets.publishing.service.gov.uk/ 
for url in doc_paths:
    if "https://assets.publishing.service.gov.uk/" in url:
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(doc_dir, os.path.basename(url))
            with open(file_path, "wb") as f:
                f.write(response.content)
    else:
        pass

# Text extraction from PDFs
# Create a list of PDF file names and text file names
pdf_list = sorted(os.listdir(doc_dir))
pdf_list = [i for i in pdf_list if ".odt" not in i]
pdf_list = [i for i in pdf_list if ".ods" not in i]
pdf_list = [i for i in pdf_list if ".txt" not in i]
pdf_list = [i for i in pdf_list if ".xlsx" not in i]
pdf_list = [i for i in pdf_list if ".docx" not in i]
pdf_list = [i for i in pdf_list if ".xlsm" not in i]
txt_list = [pdf[:-4] + ".txt" for pdf in pdf_list]

# Extracting text and saving output in dictionary
for i in range(0, len(pdf_list)):
    out = open(txt_list[i], "wt")  # open text output
    with pdfplumber.open(os.fsdecode(pdf_list[i])) as pdf:
        for pdf_page in pdf.pages:
            page_text = pdf_page.extract_text()
            out.write(page_text)
        out.close()

# Text extraction for Microsoft Word documents
for doc in os.listdir(doc_dir):
    if doc[-5:] == ".docx":
        pypandoc.convert_file(doc, "plain", outputfile = doc[:-5] + ".txt")

# Pre-processing text extracted from PDFs/Microsoft Word and matching to originating institutions
# Pre-processing txt files within pandas dataframe
# Removing documents with unextractable texts (e.g. general vesting declarations, UNCRC Bills, etc.)
doc_df["text"] = ""
txt_to_str = [x for x in os.listdir(doc_dir) if ".txt" in x]
gvd_doc = [x for x in txt_to_str if "GVD_" in x]
unextractable_text = [
    "Withdrawal_Agreement_Joint_Committee_Annual_Report_2020.txt",
    "UNCRC_-_ECLSG_References_-_Written_Case_for_the_Attorney_General_and_Advocate_General_for_Scotland__1_.txt",
    "211013_Signed_S50_Direction_-_Island_Project_School.txt",
    "hs2_gvd_deed_and_plan_48.txt",
    "hs2_gvd_deed_and_plan_39.txt",
    "S221_007_01___GVD_16_and_Plan_16_-_certified_copy.txt",
    "M162.txt",
    "dhsc-em-march-7-2022.txt",
    "A1_Development_of_the_Proposed_Scheme_v1.txt",
    "DVLA_Framework_Agreement.txt",
    "Decision_No_2_2022_Withdrawal_Agreement_Joint_Committee_-_Amendment_to_Decision_No_7_2020.txt",
    "FINAL_Declaration_on_Government_Reform.txt",
    "A1_Development_of_the_Proposed_Scheme_v2.txt",
]
unextractable_text.extend(gvd_doc)
temp_text = ""
for i in range(0, len(doc_df["url"])):
    for j in range(0, len(txt_to_str)):
        if any(x in txt_to_str[j] for x in unextractable_text):
            pass
        elif txt_to_str[j][:-4] in doc_df["url"][i]:
            del temp_text
            temp_text = pd.read_csv(txt_to_str[j], delimiter = "\n", names = ["text"])
            # concatenate all rows into one row
            temp_text["text"] = temp_text["text"].str.cat(sep = " ")
            # dataframe now redundant, replace it with one of the rows 
            temp_text = temp_text["text"][0]
            # convert string to lowercases
            temp_text = temp_text.lower()
            # translating unicode strings into normal characters
            temp_text = unicodedata.normalize("NFKD", temp_text)
            # remove all punctuation symbols, except for "&()-."
            temp_text = temp_text.translate(
                str.maketrans(
                    "",
                    "",
                    string.punctuation[:5]
                    + string.punctuation[6]
                    + string.punctuation[9:12]
                    + string.punctuation[14:],
                )
            )
            # remove excess whitespaces
            temp_text = re.sub(" +", " ", temp_text)
            doc_df["text"][i] = temp_text

# Match texts extracted from HTML docs to relevant originating institution
for i in range(0, len(doc_df["url"])):
    for j in range(0, len(html_urls)):
        if doc_df["url"][i] == html_urls[j]:
            doc_df["text"][i] = html_texts[j]

# Dropping URLs with unextractable texts
doc_df = doc_df[doc_df.text != ""]
doc_df.reset_index(drop = True, inplace = True)

# Export extracted texts as JSON file (preserve text mining work to date)
doc_df.to_json("../texts/UK_govt_policy_papers.json")