from json import load, JSONDecodeError
from os.path import exists, isfile, dirname, abspath
from os import chdir
from sys import argv
from time import sleep
from requests import post, get

def scan(file):
    file = abspath(file)
    chdir(dirname(argv[0]))
    # Load proxy settings
    if exists("proxy.json"):
        try:
            with open('proxy.json', 'r') as proxy_file:
                proxy = load(proxy_file)
        except JSONDecodeError:
            print("Error decoding proxy.json. Ensure it's a valid JSON.")
            proxy = None
    else:
        proxy = None

    if exists('key.txt'): API_KEY = open('key.txt', 'r').read()
    else:
        print('API Key not set')
        return
    FILE_PATH = file

    if not isfile(FILE_PATH):
        print("The specified file does not exist.")
        return

    def scan_file(api_key, file_path):
        url = 'https://www.virustotal.com/api/v3/files'
        headers = {'x-apikey': api_key}
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_path, file)}
                response = post(url, headers=headers, files=files, proxies=proxy)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"An error occurred while scanning the file: {e}")
            return None

    def get_report(api_key, analysis_id):
        sleep(10)
        url = f'https://www.virustotal.com/api/v3/analyses/{analysis_id}'
        headers = {'x-apikey': api_key}
        while True:
            try:
                response = get(url, headers=headers, proxies=proxy)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print("Report not ready yet, retrying...")
                    sleep(10)  # Wait before retrying
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                print(f"An error occurred while retrieving the report: {e}")
                return None

    def display_score(report):
        try:
            # Extract score from the report
            scan_results = report['data']['attributes']['results']
            stats = report['data']['attributes']['stats']
            malicious = stats['malicious']
            total = sum(stats.values())

            print(f"Malicious Score: {malicious}/{total}")

            # Display percentage
            try:
                print(str(round((malicious / total) * 100)) + '%')
            except ZeroDivisionError:
                print('0%')

            # Check specifically for Microsoft Defender's result
            microsoft_defender_result = scan_results.get('Microsoft')
            if microsoft_defender_result:
                if microsoft_defender_result['category'] == 'malicious':
                    print("Microsoft Defender flagged this file as malicious.")
                else:
                    print("Microsoft Defender did not flag this file as malicious.")
            else:
                print("No result from Microsoft Defender available.")

        except KeyError:
            print("Could not retrieve scan score from report.")

    # Scan the file
    scan_result = scan_file(API_KEY, FILE_PATH)
    if scan_result:
        analysis_id = scan_result['data']['id']
        print(f"Analysis ID: {analysis_id}")

        # Get the report using the analysis ID
        sleep(10)
        report = get_report(API_KEY, analysis_id)
        if report:
            display_score(report)