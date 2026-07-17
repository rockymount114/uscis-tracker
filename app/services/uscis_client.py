import os
import requests
from bs4 import BeautifulSoup

def fetch_case_status(receipt_number):
    """
    Fetches the actual status of a USCIS case given its receipt number.
    Returns a dict {"status": status, "detail": detail, "is_simulated": False} if successful.
    If the request fails or is blocked by Cloudflare (HTTP 403), it falls back to a deterministic 
    simulated status flagged with "is_simulated": True.
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
                    return {"status": status, "detail": detail, "is_simulated": False}
            
            # Check alternate USCIS layout
            current_status_sec = soup.find('div', class_='current-status-sec')
            if current_status_sec:
                status_text = current_status_sec.text.strip()
                if "Your current status:" in status_text:
                    status_text = status_text.replace("Your current status:", "").strip()
                return {"status": status_text, "detail": "", "is_simulated": False}
    except Exception as e:
        print(f"Error fetching status from USCIS for {receipt_number}: {e}")
        
    return get_simulated_status(receipt_number)

def get_simulated_status(receipt_number):
    # Deterministic simulated statuses using receipt number characters sum
    statuses = [
        ("Case Was Received", "On January 10, 2026, we received your case..."),
        ("Fingerprint Fee Was Received", "On January 15, 2026, we accepted the fingerprint fee..."),
        ("Case Was Updated To Show Fingerprints Were Taken", "On January 25, 2026, we updated your case to show fingerprints were taken..."),
        ("Request for Additional Evidence Was Sent", "On February 10, 2026, we sent a request for additional evidence. You must respond by May 9, 2026."),
        ("Response To USCIS' Request For Evidence Was Received", "On March 1, 2026, we received your response to our Request for Evidence..."),
        ("Case is Ready to Be Scheduled for An Interview", "On March 20, 2026, we started scheduling your interview..."),
        ("Interview Was Scheduled", "On April 5, 2026, we scheduled an interview for your case..."),
        ("Case Was Approved", "On May 12, 2026, we approved your Form..."),
        ("Card Was Mailed To Me", "On May 15, 2026, we mailed your new card. The tracking number assigned is 9205590153070156091024."),
        ("Card Was Delivered To Me By The Post Office", "On May 18, 2026, the Post Office delivered your new card. The tracking number assigned is 9205590153070156091024.")
    ]
    val = sum(ord(c) for c in receipt_number)
    status_pair = statuses[val % len(statuses)]
    return {
        "status": status_pair[0],
        "detail": status_pair[1],
        "is_simulated": True
    }
