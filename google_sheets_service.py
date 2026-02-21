"""
Enhanced Google Sheets Service for GlobleXGPT
Handles all data synchronization with Google Sheets including:
- User registrations
- Payment tracking (Razorpay)
- Promo code usage
- Failed payments
- Revenue analytics
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.script_url = os.getenv("GOOGLE_SHEETS_SCRIPT_URL")
        if not self.script_url:
            logger.warning("⚠ GOOGLE_SHEETS_SCRIPT_URL not configured")
        else:
            logger.info(f"✓ Google Sheets integration enabled")
    
    def _send_request(self, data: Dict[str, Any], method: str = "POST") -> Optional[Dict]:
        """Send request to Google Apps Script"""
        if not self.script_url:
            logger.warning("Google Sheets URL not configured, skipping sync")
            return None
        
        try:
            if method == "POST":
                response = requests.post(
                    self.script_url,
                    json=data,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
            else:  # GET
                response = requests.get(
                    self.script_url,
                    params=data,
                    timeout=10
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Google Sheets API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to sync to Google Sheets: {e}")
            return None
    
    def register_user(self, email: str, name: str, registration_method: str = "Email", 
                     ip_address: str = "", user_agent: str = "") -> bool:
        """
        Log user registration to Google Sheets
        
        Args:
            email: User email
            name: User full name
            registration_method: How they registered (Email, Google, GitHub)
            ip_address: User IP address
            user_agent: Browser user agent
        """
        data = {
            "action": "register",
            "email": email,
            "name": name,
            "registration_method": registration_method,
            "plan_type": "FREE",
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self._send_request(data)
        if result and result.get('result') == 'success':
            logger.info(f"✓ User registration logged: {email}")
            return True
        return False
    
    def log_payment_success(self, email: str, name: str, phone: str = "",
                           payment_method: str = "Razorpay", 
                           payment_details: str = "Credit/Debit Card",
                           amount: str = "499",
                           transaction_id: str = "",
                           razorpay_order_id: str = "",
                           razorpay_payment_id: str = "",
                           promo_code: str = "N/A",
                           ip_address: str = "",
                           user_agent: str = "") -> bool:
        """
        Log successful payment to Google Sheets
        
        Args:
            email: User email
            name: User name
            phone: User phone number
            payment_method: Payment method (Razorpay, Promo Code)
            payment_details: Specific payment type (Card, UPI, Wallet, NetBanking)
            amount: Payment amount in rupees
            transaction_id: Transaction ID
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            promo_code: Promo code used (if any)
            ip_address: User IP
            user_agent: Browser user agent
        """
        activation_date = datetime.now().strftime("%Y-%m-%d")
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        data = {
            "action": "payment_success",
            "email": email,
            "name": name,
            "phone": phone,
            "payment_method": payment_method,
            "payment_details": payment_details,
            "amount": amount,
            "transaction_id": transaction_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "promo_code": promo_code,
            "plan_type": "PRO",
            "activation_date": activation_date,
            "expiry_date": expiry_date,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self._send_request(data)
        if result and result.get('result') == 'success':
            logger.info(f"✓ Payment logged for {email}: ₹{amount}")
            return True
        return False
    
    def log_promo_upgrade(self, email: str, name: str, promo_code: str,
                         ip_address: str = "", user_agent: str = "") -> bool:
        """
        Log promo code upgrade to Google Sheets
        
        Args:
            email: User email
            name: User name
            promo_code: Promo code used
            ip_address: User IP
            user_agent: Browser user agent
        """
        activation_date = datetime.now().strftime("%Y-%m-%d")
        expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        data = {
            "action": "pro_upgrade",
            "email": email,
            "name": name,
            "phone": "",
            "payment_method": "Promo Code",
            "payment_details": "Promo Code Redemption",
            "amount": "0",
            "transaction_id": f"PROMO_{int(datetime.now().timestamp())}",
            "razorpay_order_id": "",
            "razorpay_payment_id": "",
            "promo_code": promo_code,
            "plan_type": "PRO",
            "activation_date": activation_date,
            "expiry_date": expiry_date,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self._send_request(data)
        if result and result.get('result') == 'success':
            logger.info(f"✓ Promo upgrade logged for {email}: {promo_code}")
            return True
        return False
    
    def log_payment_failed(self, email: str, name: str, payment_method: str = "Razorpay",
                          amount: str = "499", razorpay_order_id: str = "",
                          error_message: str = "", ip_address: str = "") -> bool:
        """
        Log failed payment to Google Sheets
        
        Args:
            email: User email
            name: User name
            payment_method: Payment method attempted
            amount: Payment amount
            razorpay_order_id: Razorpay order ID
            error_message: Error description
            ip_address: User IP
        """
        data = {
            "action": "payment_failed",
            "email": email,
            "name": name,
            "payment_method": payment_method,
            "amount": amount,
            "razorpay_order_id": razorpay_order_id,
            "error_message": error_message,
            "ip_address": ip_address,
            "timestamp": datetime.now().isoformat()
        }
        
        result = self._send_request(data)
        if result and result.get('result') == 'success':
            logger.info(f"✓ Failed payment logged for {email}")
            return True
        return False
    
    def get_pro_emails(self) -> list:
        """
        Get list of active PRO user emails from Google Sheets
        
        Returns:
            List of email addresses with active PRO status
        """
        try:
            result = self._send_request({"action": "active"}, method="GET")
            if result and isinstance(result, list):
                return [user.get('email', '').lower() for user in result if user.get('status') == 'ACTIVE']
            return []
        except Exception as e:
            logger.error(f"Failed to fetch PRO emails: {e}")
            return []
    
    def get_revenue_stats(self) -> Optional[Dict]:
        """
        Get revenue statistics from Google Sheets
        
        Returns:
            Dictionary with revenue stats or None
        """
        try:
            result = self._send_request({"action": "revenue"}, method="GET")
            if result:
                logger.info(f"✓ Revenue stats: ₹{result.get('total_revenue', 0)}")
                return result
            return None
        except Exception as e:
            logger.error(f"Failed to fetch revenue stats: {e}")
            return None
    
    # Legacy method for backward compatibility
    def sync_user(self, email: str, name: str, password: str, plan_type: str,
                  amount: str, ip_address: str, phone: str = "",
                  transaction_id: str = "", razorpay_order_id: str = "",
                  razorpay_payment_id: str = "", user_agent: str = "") -> bool:
        """
        Legacy sync method - redirects to appropriate new method based on plan_type
        """
        # Determine action based on plan_type
        if "Razorpay" in plan_type:
            return self.log_payment_success(
                email=email,
                name=name,
                phone=phone,
                payment_method="Razorpay",
                payment_details="Credit/Debit Card",
                amount=amount,
                transaction_id=transaction_id,
                razorpay_order_id=razorpay_order_id,
                razorpay_payment_id=razorpay_payment_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
        elif "Promo" in plan_type:
            promo_code = plan_type.split("-")[-1].strip() if "-" in plan_type else "UNKNOWN"
            return self.log_promo_upgrade(
                email=email,
                name=name,
                promo_code=promo_code,
                ip_address=ip_address,
                user_agent=user_agent
            )
        elif "Signup" in plan_type or "New" in plan_type:
            method = "Google" if "GOOGLE" in password else "GitHub" if "GITHUB" in password else "Email"
            return self.register_user(
                email=email,
                name=name,
                registration_method=method,
                ip_address=ip_address,
                user_agent=user_agent
            )
        else:
            # Just log as registration for other cases
            return self.register_user(
                email=email,
                name=name,
                registration_method="Login",
                ip_address=ip_address,
                user_agent=user_agent
            )

# Create singleton instance
sheets_service = GoogleSheetsService()
