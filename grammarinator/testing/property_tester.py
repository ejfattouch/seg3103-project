import json
import requests
import sys
import os

# Add the grammar directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'grammar'))

from LoginJSONGenerator import LoginJSONGenerator
from grammarinator.runtime import DefaultModel


class PropertyBasedTester:
    def __init__(self):
        self.generator = LoginJSONGenerator()
    
    def test_login_properties(self):
        """Test properties of login system"""
        for _ in range(200):
            login_data = json.loads(str(self.generator.json()))
            
            # Property 1: All requests should return valid HTTP status codes
            response = requests.post("http://localhost:8080/login", json=login_data)
            assert 200 <= response.status_code < 600, f"Invalid status code: {response.status_code}"
            
            # Property 2: Response should always be JSON or HTML
            content_type = response.headers.get('content-type', '')
            assert 'json' in content_type or 'html' in content_type, "Invalid content type"
            
            # Property 3: No sensitive data in error responses
            if response.status_code >= 400:
                assert 'password' not in response.text.lower(), "Password leaked in error"
                assert 'mongodb' not in response.text.lower(), "Database info leaked"
                
                
if __name__ == "__main__":
    tester = PropertyBasedTester()
    tester.test_login_properties()
    print("All properties tested successfully.")
    
    