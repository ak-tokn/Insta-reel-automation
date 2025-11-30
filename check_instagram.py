#!/usr/bin/env python3
"""Check Instagram API connection status."""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def check_instagram():
    """Check Instagram API access and display status."""
    
    print("=" * 50)
    print("INSTAGRAM API CONNECTION CHECK")
    print("=" * 50)
    
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    user_id = os.environ.get('INSTAGRAM_USER_ID')
    
    if not access_token:
        print("\n[ERROR] INSTAGRAM_ACCESS_TOKEN not found in secrets")
        return False
    
    if not user_id:
        print("\n[ERROR] INSTAGRAM_USER_ID not found in secrets")
        return False
    
    print("\n[OK] Credentials found in secrets")
    print(f"    User ID: {user_id}")
    print(f"    Token: {access_token[:20]}...{access_token[-10:]}")
    
    base_url = "https://graph.facebook.com/v19.0"
    
    print("\n--- Testing API Access ---")
    
    endpoint = f"{base_url}/{user_id}"
    params = {
        'access_token': access_token,
        'fields': 'id,username,account_type,media_count'
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        data = response.json()
        
        if 'error' in data:
            error = data['error']
            print(f"\n[FAILED] API Error:")
            print(f"    Type: {error.get('type', 'Unknown')}")
            print(f"    Code: {error.get('code', 'N/A')}")
            print(f"    Message: {error.get('message', 'No message')}")
            
            if 'OAuthException' in str(error.get('type', '')):
                print("\n>>> SOLUTION:")
                print("    1. Go to Meta Developer Portal: https://developers.facebook.com/apps/")
                print("    2. Select your app")
                print("    3. Check 'App Review' - your app may need verification")
                print("    4. Check 'Settings > Basic' - ensure app is in Live mode")
                print("    5. Go to Instagram Graph API > Generate a new token")
                print("    6. Update INSTAGRAM_ACCESS_TOKEN in Replit Secrets")
            
            return False
        
        print(f"\n[SUCCESS] Connected to Instagram!")
        print(f"    Username: @{data.get('username', 'N/A')}")
        print(f"    Account Type: {data.get('account_type', 'N/A')}")
        print(f"    Media Count: {data.get('media_count', 0)}")
        
        print("\n--- Testing Permissions ---")
        perm_endpoint = f"{base_url}/me/permissions"
        perm_params = {'access_token': access_token}
        perm_response = requests.get(perm_endpoint, params=perm_params, timeout=30)
        perm_data = perm_response.json()
        
        if 'data' in perm_data:
            print("    Granted permissions:")
            for perm in perm_data.get('data', []):
                status = "[OK]" if perm.get('status') == 'granted' else "[X]"
                print(f"      {status} {perm.get('permission')}")
        
        print("\n--- Testing Content Publish Permission ---")
        content_publish_url = f"{base_url}/{user_id}/content_publishing_limit"
        cp_params = {
            'access_token': access_token,
            'fields': 'quota_usage'
        }
        cp_response = requests.get(content_publish_url, params=cp_params, timeout=30)
        cp_data = cp_response.json()
        
        if 'error' in cp_data:
            print(f"    [WARNING] Could not check publishing limit: {cp_data['error'].get('message', 'Unknown')}")
        else:
            usage = cp_data.get('quota_usage', 0)
            print(f"    Quota usage today: {usage}/25 posts")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Network error: {e}")
        return False

if __name__ == "__main__":
    success = check_instagram()
    print("\n" + "=" * 50)
    if success:
        print("STATUS: Instagram API is working!")
    else:
        print("STATUS: Instagram API access BLOCKED or not configured")
    print("=" * 50)
    sys.exit(0 if success else 1)
