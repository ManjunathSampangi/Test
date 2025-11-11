"""
Authentication Helper Script
Helps users generate Fyers access token
"""

import os
from dotenv import load_dotenv
from fyers_auth import FyersAuth

load_dotenv()


def main():
    """Helper script to generate Fyers access token"""
    print("=" * 60)
    print("Fyers Trading Bot - Authentication Helper")
    print("=" * 60)
    print()
    
    # Check if credentials exist
    app_id = os.getenv('FYERS_APP_ID')
    secret_key = os.getenv('FYERS_SECRET_KEY')
    
    if not app_id or not secret_key:
        print("ERROR: FYERS_APP_ID and FYERS_SECRET_KEY must be set in .env file")
        print("Please create a .env file with your Fyers credentials")
        return
    
    # Initialize auth
    auth = FyersAuth()
    
    print("Step 1: Generating authorization URL...")
    auth_url = auth.generate_auth_code()
    print()
    print("Please visit the following URL in your browser:")
    print(auth_url)
    print()
    print("After authorizing, you will be redirected to a URL.")
    print("Copy the 'auth_code' parameter from the redirected URL.")
    print()
    
    # Get auth code from user
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("ERROR: Authorization code is required")
        return
    
    print()
    print("Step 2: Generating access token...")
    access_token = auth.generate_access_token(auth_code)
    
    if access_token:
        print()
        print("=" * 60)
        print("SUCCESS! Access token generated.")
        print("=" * 60)
        print()
        print("Add this to your .env file:")
        print(f"FYERS_ACCESS_TOKEN={access_token}")
        print()
        print("Or update your .env file with the access token above.")
    else:
        print()
        print("ERROR: Failed to generate access token")
        print("Please check your authorization code and try again.")


if __name__ == "__main__":
    main()
