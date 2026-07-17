import os
import requests
from bs4 import BeautifulSoup

def fetch_case_status(receipt_number):
    """
    Fetches the actual status of a USCIS case given its receipt number.
    Returns a dict {"status": status, "detail": detail} if successful, or None if it fails.
    """
    uscis_url = os.getenv("USCIS_API_URL", "https://egov.uscis.gov/casestatus/mycasestatus.do")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(
            uscis_url, 
            data={'appReceiptNum': receipt_number, 'initCaseSearch': 'CHECK STATUS'}, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Check for standard status headers
            status_div = soup.find('div', class_='rows text-center')
            if status_div:
                h1_text = status_div.find('h1')
                if h1_text:
                    status = h1_text.text.strip()
                    detail = ""
                    p_text = status_div.find('p')
                    if p_text:
                        detail = p_text.text.strip()
                    return {"status": status, "detail": detail}
            
            # Check alternate USCIS layout
            current_status_sec = soup.find('div', class_='current-status-sec')
            if current_status_sec:
                status_text = current_status_sec.text.strip()
                if "Your current status:" in status_text:
                    status_text = status_text.replace("Your current status:", "").strip()
                return {"status": status_text, "detail": ""}
    except Exception as e:
        print(f"Error fetching status from USCIS for {receipt_number}: {e}")
        
    return None
