import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

counter = 0
load_dotenv('.env')
#  ... ...፣ .{1,2} .{2,4}፣ \d\d\d\d \(ኤፍ .{1,2} .\)
project_folder_name = os.getenv("PROJECT_FOLDERNAME")
base_url = os.getenv("BASE_URL")
found_url_file_name = os.path.join(project_folder_name, os.getenv("FOUND_URLS_FILENAME"))
scraped_url_file_name = os.path.join(project_folder_name, os.getenv("SCRAPED_URLS_FILENAME"))
downloaded_files_folder_name = os.path.join(project_folder_name, os.getenv("DOWNLOADED_FILES_FOLDERNAME"))

lock = threading.Lock()


def ensure_folders_and_files():
    os.makedirs(downloaded_files_folder_name, exist_ok=True)
    for f in [found_url_file_name, scraped_url_file_name]:
        if not os.path.exists(f):
            with open(f, 'w') as file:
                pass


def read_lines(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def append_line_if_not_exists(filepath, line):
    lines = read_lines(filepath)
    if line in lines:
        return
    with open(filepath, 'a') as f:
        f.write(line + '\n')


def get_start_index(found, scraped):
    if not scraped:
        return 0
    last = scraped[-1]
    if last in found:
        idx = found.index(last)
        return idx + 1 if idx + 1 < len(found) else len(found)
    return len(found)


def extract_links_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if href.startswith('/'):
            href = base_url + href[1:]
        if href.startswith(base_url):
            links.append(href)
    return links


def scrape_and_save(url, index):
    global counter
    counter += 1
    print("COUNTER", counter)
    print(f"Scraping: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Request error for {url}: {e}")
        return []

    file_name = f"{index}.html"
    file_path = os.path.join(downloaded_files_folder_name, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(resp.text)

    links_live = extract_links_from_html(resp.text)
    with open(file_path, 'r', encoding='utf-8') as f:
        links_local = extract_links_from_html(f.read())

    return links_live + links_local


def store_urls(urls):
    for url in urls:
        append_line_if_not_exists(found_url_file_name, url)


def worker(job_queue):
    while True:
        try:
            job = job_queue.pop(0)
        except IndexError:
            break
        print(f"[Worker] Scraping: {job['url']}")
        new_links = scrape_and_save(job['url'], job['index'])

        try:
            new_links = scrape_and_save(job['url'], job['index'])
        except Exception as e:
            print(f"[Worker] Error scraping {job['url']}: {e}")
            new_links = []

        with lock:
            store_urls(new_links)
            append_line_if_not_exists(scraped_url_file_name, job['url'])



def main():
    if not base_url:
        print("BASE_URL is not set in the environment variables")
        return

    print("Base URL:", base_url)

    ensure_folders_and_files()
    store_urls([base_url])

    while True:
        found_urls = read_lines(found_url_file_name)
        scraped_urls = read_lines(scraped_url_file_name)

        print(f"STATUS:\n\tTOTAL={len(found_urls)}\n\tSCRAPED={len(scraped_urls)}\n\tUNSCRAPED={len(found_urls) - len(scraped_urls)}")
        if len(found_urls) == len(scraped_urls):
            print("Scraping completed successfully ✅")
            break

        start_index = get_start_index(found_urls, scraped_urls)
        if start_index >= len(found_urls):
            print("Scraping completed successfully ✅")
            break

        job_queue = [{"url": found_urls[i], "index": i} for i in range(start_index, len(found_urls))]

        threads = []
        num_workers = 10
        for _ in range(min(num_workers, len(job_queue))):
            t = threading.Thread(target=worker, args=(job_queue,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        time.sleep(1)


if __name__ == "__main__":
    main()
