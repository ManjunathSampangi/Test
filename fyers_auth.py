"""
Fyers Authentication Module
Handles authentication and token management with Fyers API
"""

import os
import json
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FyersAuth:
    def __init__(self, app_id=None, secret_key=None, redirect_uri=None):
        """
        Initialize Fyers Authentication
        
        Args:
            app_id: Fyers App ID
            secret_key: Fyers Secret Key
            redirect_uri: Redirect URI registered with Fyers
        """
        self.app_id = app_id or os.getenv('FYERS_APP_ID')
        self.secret_key = secret_key or os.getenv('FYERS_SECRET_KEY')
        self.redirect_uri = redirect_uri or os.getenv('FYERS_REDIRECT_URI', 'https://127.0.0.1/')
        self.access_token = os.getenv('FYERS_ACCESS_TOKEN')
        self.base_url = "https://api.fyers.in/v2"
        self.session = None
        
    def generate_auth_code(self):
        """
        Generate authorization code URL
        User needs to visit this URL and authorize the app
        """
        auth_url = (
            f"https://api.fyers.in/v2/oauth/authorize?"
            f"client_id={self.app_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"state=sample_state"
        )
        logger.info(f"Visit this URL to authorize: {auth_url}")
        return auth_url
    
    def generate_access_token(self, auth_code):
        """
        Generate access token using authorization code
        
        Args:
            auth_code: Authorization code received from redirect
            
        Returns:
            Access token string
        """
        url = f"{self.base_url}/oauth/validate-authcode"
        
        data = {
            "grant_type": "authorization_code",
            "appIdHash": self.secret_key,
            "code": auth_code
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('s') == 'ok':
                self.access_token = result['access_token']
                logger.info("Access token generated successfully")
                return self.access_token
            else:
                logger.error(f"Failed to generate access token: {result}")
                return None
        except Exception as e:
            logger.error(f"Error generating access token: {str(e)}")
            return None
    
    def create_session(self, access_token=None):
        """
        Create Fyers session with access token
        
        Args:
            access_token: Access token (uses stored token if not provided)
            
        Returns:
            Fyers session object
        """
        from fyers_apiv2 import fyersModel
        
        token = access_token or self.access_token
        if not token:
            raise ValueError("Access token is required. Please generate one first.")
        
        self.session = fyersModel.SessionModel(
            client_id=self.app_id,
            redirect_uri=self.redirect_uri,
            response_type="code",
            secret_key=self.secret_key,
            grant_type="authorization_code"
        )
        
        self.session.set_token(token)
        logger.info("Fyers session created successfully")
        return self.session
    
    def get_profile(self):
        """
        Get user profile information
        
        Returns:
            User profile data
        """
        if not self.session:
            self.create_session()
        
        try:
            profile = self.session.get_profile()
            logger.info("Profile fetched successfully")
            return profile
        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return None
    
    def is_authenticated(self):
        """
        Check if session is authenticated
        
        Returns:
            Boolean indicating authentication status
        """
        try:
            profile = self.get_profile()
            return profile is not None and profile.get('s') == 'ok'
        except:
            return False
