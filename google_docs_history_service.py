"""
GlobleXGPT Google Docs History Logger
Service to sync search history with Google Docs using the 100-tab organization system.
"""

import os
import requests
import logging
import sys
import io
from datetime import datetime

# Handle Windows terminal encoding for emojis
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

logger = logging.getLogger(__name__)

class GoogleDocsHistoryService:
    def __init__(self):
        self.script_url = os.getenv("GOOGLE_DOCS_HISTORY_URL")
        if not self.script_url:
            logger.warning("⚠ GOOGLE_DOCS_HISTORY_URL not configured in .env")
        else:
            logger.info("✓ Google Docs History Service initialized")

    def log_search(self, email, query, response_text):
        """
        Sends search history data to the Google Docs Apps Script.
        """
        # Always re-check the URL in case it was added after startup
        url = os.getenv("GOOGLE_DOCS_HISTORY_URL")
        if not url:
            logger.warning("🔍 Google Docs History Error: URL not found in .env. Please restart server.")
            return False

        # Prepare payload
        data = {
            "email": email or "Guest",
            "query": query or "N/A",
            "response": response_text or "N/A",
            "timestamp": datetime.now().isoformat()
        }

        try:
            logger.info(f"📤 Sending history to Google Docs: {email}...")
            
            # Use json=data to ensure proper content-type and encoding
            resp = requests.post(
                url, 
                json=data, 
                timeout=12,
                allow_redirects=True
            )
            
            # Log the status for debugging
            logger.info(f"💾 Google Docs Response Status: {resp.status_code}")
            
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    if result.get('result') == 'success':
                        logger.info(f"✅ History successfully logged: {result.get('message')}")
                        return True
                    else:
                        logger.error(f"❌ Google Docs Script Error: {result.get('message')}")
                        print(f"DEBUG: Script Error Message: {result.get('message')}")
                        if 'error' in result: print(f"DEBUG: Detailed Error: {result['error']}")
                except Exception as e:
                    logger.error(f"❌ Failed to parse response from Google Docs: {resp.text[:500]}")
                    print(f"DEBUG: Full Response Text: {resp.text}")
            else:
                logger.error(f"❌ Google Docs HTTP Error: {resp.status_code}")
                print(f"DEBUG: HTTP Error Body: {resp.text}")
                
        except Exception as e:
            logger.error(f"❌ Network error while syncing to Google Docs: {e}")
            import traceback
            traceback.print_exc()
        
        return False

# Singleton instance
docs_history_service = GoogleDocsHistoryService()
