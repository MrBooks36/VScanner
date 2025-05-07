from json import load, JSONDecodeError
from os.path import exists, isfile, dirname, abspath
from os import chdir, getcwd
from sys import argv
from time import sleep
from requests import post, get
cwd = getcwd()
def log(text):
    with open('log.tmp', 'a') as file:
        file.write(f'{text}\n')

def scan_with_virustotal(file_path, api_key_file='key.txt', proxy_file='proxy.json'):
    """
    Scans a file using VirusTotal and rescans if no result from Microsoft Defender is available.

    :param file_path: Path to the file to be scanned.
    :param api_key_file: Path to the file containing the API key.
    :param proxy_file: Path to the JSON file containing the proxy configuration.
    """
    def load_proxy(proxy_file):
        """Load proxy settings if the file exists."""
        if exists(proxy_file):
            try:
                with open(proxy_file, 'r') as proxy_fp:
                    return load(proxy_fp)
            except JSONDecodeError:
                log(f"Error decoding {proxy_file}. Ensure it's a valid JSON.")
        return None

    def load_api_key(api_key_file):
        """Load the API key."""
        if exists(api_key_file):
            with open(api_key_file, 'r') as key_fp:
                return key_fp.read().strip()
        else:
            log(f"API Key not set in {api_key_file}")
            return None

    def scan_file(api_key, file_path, proxy):
        """Send a file to VirusTotal for scanning."""
        url = 'https://www.virustotal.com/api/v3/files'
        headers = {'x-apikey': api_key}
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_path, file)}
                response = post(url, headers=headers, files=files, proxies=proxy)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 413:
                log('File too large')
                return None
                
            else:
                log(f"Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            log(f"An error occurred while scanning the file: {e}")
            return None

    def get_report(api_key, analysis_id, proxy):
        """Retrieve the scan report from VirusTotal."""
        sleep(10)
        url = f'https://www.virustotal.com/api/v3/analyses/{analysis_id}'
        headers = {'x-apikey': api_key}
        while True:
            try:
                response = get(url, headers=headers, proxies=proxy)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    log("Report not ready yet, retrying...")
                    sleep(10)  # Wait before retrying
                else:
                    log(f"Error: {response.status_code} - {response.text}")
                    return None
            except Exception as e:
                log(f"An error occurred while retrieving the report: {e}")
                return None

    def display_score(report):
        """Display the malicious score of the file."""
        try:
            scan_results = report['data']['attributes']['results']
            stats = report['data']['attributes']['stats']
            malicious = stats['malicious']
            total = sum(stats.values())

            log(f"Malicious Score: {malicious}/{total}")
            
            # Display percentage
            try:
                percentage = round((malicious / total) * 100)
                log(f"{percentage}%")
            except ZeroDivisionError:
                percentage = 0
                log('0%')

            # Return Microsoft Defender's result 
            return [scan_results.get('Microsoft'), percentage, f"{malicious}/{total}"]
        except KeyError:
            log("Could not retrieve scan score from report.")
            return None

    # Load API key and proxy
    chdir(dirname(argv[0]))
    log(file_path)
    api_key = load_api_key(api_key_file)
    proxy = load_proxy(proxy_file)

    if not api_key or not isfile(file_path):
        log("Exiting due to missing API key or invalid file.")
        return "Exiting due to missing API key or invalid file."

    file_path = abspath(file_path)

    # Scan the file and retrieve report
    while True:
        scan_result = scan_file(api_key, file_path, proxy)
        if scan_result != None:
            analysis_id = scan_result['data']['id']
            log(f"Analysis ID: {analysis_id}")

            # Get the report using the analysis ID
            report = get_report(api_key, analysis_id, proxy)
            if report:
                defender_result = display_score(report)
                if defender_result[0]:
                    # Display Microsoft Defender's result
                    if defender_result[0]['category'] == 'malicious':
                        log("Microsoft Defender flagged this file as malicious.")
                    else:
                        log("Microsoft Defender did not flag this file as malicious.")
                        return defender_result
                    break
                else:
                    log("No result from Microsoft Defender available. Rescanning...")
        else: return        
