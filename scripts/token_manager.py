"""
Instagram Token Manager for StoicAlgo
Handles automatic refresh of long-lived Instagram access tokens.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.logger import get_logger

logger = get_logger("TokenManager")

ENV_PATH = project_root / ".env"


class TokenManager:
    """Manages Instagram access token lifecycle."""
    
    GRAPH_API_VERSION = "v18.0"
    GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    
    def __init__(self):
        load_dotenv(ENV_PATH)
        self.app_id = os.getenv("META_APP_ID")
        self.app_secret = os.getenv("META_APP_SECRET")
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        
        if not all([self.app_id, self.app_secret]):
            raise ValueError("META_APP_ID and META_APP_SECRET must be set in .env")
    
    def check_token_validity(self) -> dict:
        """Check if current token is valid and get expiration info."""
        
        url = f"{self.GRAPH_API_BASE}/debug_token"
        params = {
            "input_token": self.access_token,
            "access_token": f"{self.app_id}|{self.app_secret}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if "data" in data:
                token_data = data["data"]
                is_valid = token_data.get("is_valid", False)
                expires_at = token_data.get("expires_at", 0)
                
                if expires_at:
                    expiry_date = datetime.fromtimestamp(expires_at)
                    days_remaining = (expiry_date - datetime.now()).days
                else:
                    expiry_date = None
                    days_remaining = -1
                
                return {
                    "valid": is_valid,
                    "expires_at": expiry_date,
                    "days_remaining": days_remaining,
                    "scopes": token_data.get("scopes", [])
                }
            else:
                error = data.get("error", {})
                logger.error(f"Token debug failed: {error.get('message', 'Unknown error')}")
                return {"valid": False, "error": error.get("message")}
                
        except Exception as e:
            logger.error(f"Failed to check token: {str(e)}")
            return {"valid": False, "error": str(e)}
    
    def refresh_token(self) -> bool:
        """
        Refresh the long-lived access token.
        Long-lived tokens can be refreshed if they haven't expired yet.
        Returns True if successful.
        """
        
        url = f"{self.GRAPH_API_BASE}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": self.access_token
        }
        
        try:
            logger.info("Attempting to refresh Instagram access token...")
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if "access_token" in data:
                new_token = data["access_token"]
                expires_in = data.get("expires_in", 0)
                
                # Update .env file
                set_key(str(ENV_PATH), "INSTAGRAM_ACCESS_TOKEN", new_token)
                self.access_token = new_token
                
                expiry_days = expires_in // 86400
                logger.info(f"✓ Token refreshed successfully! Valid for {expiry_days} days")
                
                return True
            else:
                error = data.get("error", {})
                error_msg = error.get("message", "Unknown error")
                logger.error(f"Token refresh failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return False
    
    def ensure_valid_token(self) -> bool:
        """
        Check token and refresh if needed.
        Called automatically before posting.
        Returns True if we have a valid token.
        """
        
        status = self.check_token_validity()
        
        if not status.get("valid"):
            logger.warning("Token is invalid or expired")
            # Try to refresh anyway - might work if recently expired
            return self.refresh_token()
        
        days_remaining = status.get("days_remaining", 0)
        
        # Refresh if less than 7 days remaining
        if days_remaining < 7:
            logger.info(f"Token expires in {days_remaining} days, refreshing proactively...")
            return self.refresh_token()
        
        logger.info(f"Token is valid for {days_remaining} more days")
        return True


def refresh_token_cli():
    """CLI entry point for token refresh."""
    
    print("\n" + "="*50)
    print("INSTAGRAM TOKEN MANAGER")
    print("="*50 + "\n")
    
    try:
        manager = TokenManager()
        
        # Check current status
        print("Checking current token status...")
        status = manager.check_token_validity()
        
        if status.get("valid"):
            print(f"✓ Token is currently VALID")
            if status.get("expires_at"):
                print(f"  Expires: {status['expires_at']}")
                print(f"  Days remaining: {status['days_remaining']}")
        else:
            print(f"✗ Token is INVALID or EXPIRED")
            if status.get("error"):
                print(f"  Error: {status['error']}")
        
        print("\nAttempting refresh...")
        
        if manager.refresh_token():
            print("\n✓ SUCCESS! Token has been refreshed.")
            
            # Verify new token
            new_status = manager.check_token_validity()
            if new_status.get("valid"):
                print(f"  New expiry: {new_status.get('expires_at')}")
                print(f"  Valid for: {new_status.get('days_remaining')} days")
        else:
            print("\n✗ FAILED to refresh token.")
            print("\nYou may need to generate a new token manually:")
            print("1. Go to https://developers.facebook.com/tools/explorer/")
            print("2. Select your app and generate a new User Token")
            print("3. Update INSTAGRAM_ACCESS_TOKEN in .env")
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    
    print("\n" + "="*50 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(refresh_token_cli())
