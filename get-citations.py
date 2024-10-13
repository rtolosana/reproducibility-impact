import json
import requests
import csv
import re
from pyalex import Works
import os  # Import os to handle file paths

def is_doi(doi):
    doi_pattern = re.compile(r'^(https?://)?doi\.org/10\.\d{4,}/\S+$')
    return bool(doi_pattern.match(doi))

def extract_scedition_from_url(url):
    match = re.search(r'sc(\d+)', url)
    if match:
        return match.group(0)
    else:
        return ""
        
def get_citations_opencitations(key):
    api_url = f"https://opencitations.net/index/api/v1/citations/{key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        opencitationsdata = response.json()
        citations = len(opencitationsdata)
        return citations
    else:
        error_message = f"Failed to fetch citations for {key}. Status code: {response.status_code}"
        return error_message

def get_citations_openalex(key):
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
        print("An error occurred: ", str(e))
        return str(e)
    
def fetch_citations_from_url(url, get_citations_function):
    citations_table = {}
    dblpresponse = requests.get(url)
    if dblpresponse.status_code == 200:
        data = json.loads(dblpresponse.text)
        n = int(data['result']['hits']['@total'])
        paper_citations = {}
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

# Ensure the dataset directory exists
os.makedirs('dataset', exist_ok=True)

filename = 'dataset/dblp-urls-sc.txt'

with open(filename, "r") as file:
    for line in file:
        url = line.strip()
        print("*****************************************************************************************************")
        print("Retrieving citations from ", url, " with openalex")
        result_table = fetch_citations_from_url(url, get_citations_openalex)
        
        scedition = extract_scedition_from_url(url)
        csv_filename = os.path.join('dataset', f'{scedition}_citations.csv')  # Save in dataset folder
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['DOI', 'Citations'])  # Write header row
            for doi, citations in result_table.items():
                csv_writer.writerow([doi, citations])

        print(f'Results for URL {url} written to {csv_filename}\n')

