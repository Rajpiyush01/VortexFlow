# analyzer.py
# This module contains all the logic for parsing HTML files and analyzing links.

import os
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urlparse
from config import TERABOX_DOMAINS
# NEW: Import the function to load our banned links list
from session_manager import load_banned_links

def _categorize_link(url):
    """Categorizes a URL based on its domain."""
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        if any(d in domain for d in TERABOX_DOMAINS):
            return "TeraBox"
        if "t.me" in domain or "telegram" in domain: return "Telegram"
        if "instagram.com" in domain: return "Instagram"
        return domain if domain else "Other"
    except:
        return "Invalid URL"

def analyze_html_files(file_paths):
    """
    Parses a list of HTML files, extracts all links, categorizes them,
    and creates a structured list of download jobs.
    """
    # NEW: Load the list of banned links at the start of the analysis
    banned_links = load_banned_links()
    
    all_raw_links = []
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "lxml")
                message_bodies = soup.find_all('div', class_='text')
                for message in message_bodies:
                    links = [a['href'] for a in message.find_all('a', href=True)]
                    all_raw_links.extend(links)
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")

    # UPGRADED: Filter out banned links from the raw list
    filtered_raw_links = [link for link in all_raw_links if link not in banned_links]

    unique_links = sorted(list(set(filtered_raw_links)))
    duplicate_count = len(filtered_raw_links) - len(unique_links)
    
    download_jobs = []
    terabox_links_in_jobs = set()
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "lxml")
                message_bodies = soup.find_all('div', class_='text')
                for i, message in enumerate(message_bodies):
                    links_in_message = sorted(list(set([a['href'] for a in message.find_all('a', href=True)])))
                    # UPGRADED: Ensure we only process non-banned TeraBox links
                    terabox_links = [link for link in links_in_message if _categorize_link(link) == 'TeraBox' and link not in banned_links]
                    if not terabox_links: continue
                    
                    unique_terabox_links_in_message = [l for l in terabox_links if l not in terabox_links_in_jobs]
                    if not unique_terabox_links_in_message: continue
                    
                    folder_name = ""
                    if len(unique_terabox_links_in_message) == 1:
                        link_tag = message.find('a', href=unique_terabox_links_in_message[0])
                        link_text = link_tag.text.strip().replace('\n', ' ') if link_tag else ""
                        safe_name = "".join([c for c in link_text if c.isalnum() or c in (' ', '-')]).rstrip()
                        folder_name = safe_name if safe_name else f"Single_Download_{os.path.basename(file_path)}_{i+1}"
                    else:
                        folder_name = f"Message_Group_{os.path.basename(file_path)}_{i+1}"

                    job = {"source_file": os.path.basename(file_path), 
                           "links": unique_terabox_links_in_message,
                           "type": "SINGLE" if len(unique_terabox_links_in_message) == 1 else "MULTI",
                           "folder_name": folder_name}
                    download_jobs.append(job)
                    terabox_links_in_jobs.update(unique_terabox_links_in_message)
        except Exception as e:
            print(f"Error during job creation for {os.path.basename(file_path)}: {e}")

    return {
        "raw_count": len(all_raw_links),
        "banned_count": len(all_raw_links) - len(filtered_raw_links), # NEW: Stat for banned links
        "duplicate_count": duplicate_count,
        "unique_links": unique_links,
        "terabox_count": len(terabox_links_in_jobs),
        "download_jobs": download_jobs
    }
