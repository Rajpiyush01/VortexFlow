# core/analyzer.py
# This module contains all the logic for parsing HTML files and analyzing links.

import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# We will assume these are correctly imported from your other modules
from .config import TERABOX_DOMAINS
from .session_manager import load_banned_links

def _categorize_link(url: str) -> str:
    """
    Categorizes a URL based on its domain.

    Args:
        url (str): The URL to categorize.

    Returns:
        str: The category of the URL (e.g., "TeraBox", "Telegram", or the domain name).
    """
    try:
        domain = urlparse(url).netloc.replace("www.", "")
        if any(d in domain for d in TERABOX_DOMAINS):
            return "TeraBox"
        if "t.me" in domain or "telegram" in domain:
            return "Telegram"
        # Add any other special domains here
        return domain if domain else "Other"
    except (ValueError, AttributeError):
        return "Invalid URL"

def analyze_html_files(file_paths: list[str]) -> dict:
    """
    Parses a list of HTML files, extracts all links, filters them,
    and creates a structured list of unique download jobs for TeraBox links.

    This function reads each file only once for improved efficiency.

    Args:
        file_paths (list[str]): A list of paths to the HTML files.

    Returns:
        dict: A dictionary containing comprehensive statistics and the list of download jobs.
    """
    print("[Analyzer] Starting analysis...")
    banned_links = load_banned_links()
    
    all_raw_links = []
    download_jobs = []
    terabox_links_already_in_jobs = set()

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "lxml")
            
            # Find all message containers in the Telegram export
            message_bodies = soup.find_all('div', class_='text')
            
            for i, message in enumerate(message_bodies):
                # 1. Extract all links from the current message
                links_in_message = [a['href'] for a in message.find_all('a', href=True)]
                if not links_in_message:
                    continue
                
                all_raw_links.extend(links_in_message)
                
                # 2. Filter for unique, non-banned TeraBox links for this specific message
                terabox_links_in_message = sorted(list(set(
                    link for link in links_in_message 
                    if _categorize_link(link) == 'TeraBox' and link not in banned_links
                )))
                
                if not terabox_links_in_message:
                    continue

                # 3. Ensure these links haven't already been added from a previous message (session-wide uniqueness)
                unique_new_links = [link for link in terabox_links_in_message if link not in terabox_links_already_in_jobs]
                
                if not unique_new_links:
                    continue
                
                # 4. Generate a smart folder name for this job
                folder_name = ""
                # If there's only one new link, use its text for the folder name
                if len(unique_new_links) == 1:
                    link_tag = message.find('a', href=unique_new_links[0])
                    link_text = link_tag.text.strip().replace('\n', ' ') if link_tag else ""
                    # Sanitize the text to create a valid folder name
                    safe_name = "".join([c for c in link_text if c.isalnum() or c in (' ', '-')]).rstrip()
                    folder_name = safe_name if safe_name else f"Single_Download_{os.path.basename(file_path)}_{i+1}"
                else:
                    # If there are multiple new links, create a generic group name
                    folder_name = f"Message_Group_{os.path.basename(file_path)}_{i+1}"

                # 5. Create the download job dictionary
                job = {
                    "source_file": os.path.basename(file_path), 
                    "links": unique_new_links,
                    "type": "SINGLE" if len(unique_new_links) == 1 else "MULTI",
                    "folder_name": folder_name
                }
                download_jobs.append(job)
                
                # 6. Add the processed links to our set to prevent future duplicates
                terabox_links_already_in_jobs.update(unique_new_links)

        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")

    # --- Final Statistics Calculation ---
    filtered_raw_links = [link for link in all_raw_links if link not in banned_links]
    unique_links = sorted(list(set(filtered_raw_links)))
    
    print(f"[Analyzer] Analysis complete. Found {len(terabox_links_already_in_jobs)} unique TeraBox links to download.")

    return {
        "raw_count": len(all_raw_links),
        "banned_count": len(all_raw_links) - len(filtered_raw_links),
        "duplicate_count": len(filtered_raw_links) - len(unique_links),
        "unique_links": unique_links,
        "terabox_count": len(terabox_links_already_in_jobs),
        "download_jobs": download_jobs
    }