import json
import requests
import csv
import re
from pyalex import Works

def is_doi(doi):
    doi_pattern = re.compile(r'^(https?://)?doi\.org/10\.\d{4,}/\S+$')
    return bool(doi_pattern.match(doi))

def extract_scedition_from_url(url):
    """
    Extracts a substring following the pattern 'sc' followed by digits from the given URL.

    Args:
    - url (str): The URL containing the substring.

    Returns:
    - str: The extracted substring if found, otherwise an empty string.
    """
    # Use regular expression to extract 'sc' followed by digits
    match = re.search(r'sc(\d+)', url)

    # Check if a match is found
    if match:
        return match.group(0)
    else:
        return ""
        
def get_citations_opencitations(key):
    """
    Retrieve the number of citations for a paper based on its DOI using OpenCitations API.

    Args:
        key (str): The DOI or the title of the paper.

    Returns:
        int: The number of citations for the paper.
        str: An error message if citations couldn't be retrieved.
    """
    # OpenCitations API URL
    api_url = f"https://opencitations.net/index/api/v1/citations/{key}"

    # Send a GET request to the OpenCitations API
    response = requests.get(api_url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        opencitationsdata = response.json()
        citations = len(opencitationsdata)
        return citations
    else:
        error_message = f"Failed to fetch citations for {key}. Status code: {response.status_code}"
        return error_message

def get_citations_openalex(key):
    """
    Retrieve the number of citations for a paper based on its DOI using OpenCitations API.

    Args:
        key (str): The DOI or the title of the paper or the title

    Returns:
        int: The number of citations for the paper.
        str: An error message if citations couldn't be retrieved.
    """
    try:
        if is_doi(key):
            specific_work = Works()[key]
        else:
            words = re.findall(r'\b\w+\b', key)
            parsed_key = ' '.join(words)
            specific_work_array = Works().search_filter(title=parsed_key).get()
            specific_work = specific_work_array[0]
        return specific_work['cited_by_count']
    except Exception as e:
        print("An error ocurred: ", str(e))
        return str(e)
    
def fetch_citations_from_url(url, get_citations_function):
    citations_table = {}

    dblpresponse = requests.get(url)

    # Check if the request was successful (status code 200)
    if dblpresponse.status_code == 200:
        data = json.loads(dblpresponse.text)

        n = int(data['result']['hits']['@total'])
        paper_citations = {}  # key -> doi, value -> number of citations

        for i in range(n):
            try:
                doi = data['result']['hits']['hit'][i]['info']['ee']

                if is_doi(doi):
                    result_citations = get_citations_function(doi)
                else:
                    title = data['result']['hits']['hit'][i]['info']['title']
                    result_citations = get_citations_function(title)

                if isinstance(result_citations, int):
                    paper_citations[doi] = result_citations
                    print("Num of citations for ", doi, " record ", i, ": ", result_citations)
                else:
                    print("Num of citations not found at ", url, " record ", i, " found: ", result_citations)
            except KeyError:
                print("DOI not found at ", url, " record ", i, ": Trying now with title")
                try:
                    title = data['result']['hits']['hit'][i]['info']['title']
                    result_citations = get_citations_function(title)
                    if isinstance(result_citations, int):
                        paper_citations[title] = result_citations
                        print("Num of citations for ", doi, " record ", i, ": ", result_citations)
                    else:
                        print("Num of citations not found at ", url, " record ", i)
                except Exception as e:
                    print("An error occurred: ", str(e))
        citations_table = paper_citations
    else:
        print("Error, no response from dblp")

    return citations_table

filename = 'dblp-urls-sc.txt'

with open(filename, "r") as file:
    for line in file:
        # Use strip to remove leading/trailing whitespaces, if any
        url = line.strip()
        print("*****************************************************************************************************")
        print("Retrieving citations from ", url, " with openalex")
        # Call fetch_citations_from_url for each line with get_citations_openalex
        result_table = fetch_citations_from_url(url, get_citations_openalex)
        
        # Extract the name of the SC edition
        scedition = extract_scedition_from_url(url)

        # Write the result_table to a CSV file
        csv_filename = f'{scedition}_citations.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['DOI', 'Citations'])  # Write header row
            for doi, citations in result_table.items():
                csv_writer.writerow([doi, citations])

        print(f'Results for URL {url} written to {csv_filename}\n')
        

