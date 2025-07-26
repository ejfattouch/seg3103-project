import json
import requests
import random
import os
import sys
# Add the grammar directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'grammar'))

from LoginJSONGenerator import LoginJSONGenerator
from grammarinator.runtime import DefaultModel

class LoginMutationTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.generator = LoginJSONGenerator(model=DefaultModel())
        
    def generate_valid_baseline(self, count=100):
        """Generate valid login attempts as baseline"""
        valid_cases = []
        for _ in range(count):
            login_json = self.generator.json()
            valid_cases.append(json.loads(str(login_json)))
        return valid_cases
    
    def mutate_email(self, email):
        """Apply mutations to email field"""
        mutations = [
            email.replace('@', ''),  # Remove @
            email.replace('.', ''),  # Remove domain extension
            email + '@extra.com',    # Double domain
            email.replace('@', '@@'), # Double @
            '',                      # Empty email
            'a' * 1000,             # Buffer overflow
            email.replace('@', '\n@'), # Newline injection
        ]
        return random.choice(mutations)
    
    def mutate_password(self, password):
        """Apply mutations to password field"""
        mutations = [
            '',                      # Empty password
            'a',                     # Too short
            'a' * 1000,             # Too long
            password + '\x00',       # Null byte
            password.replace('a', '<script>'), # XSS
            "'; DROP TABLE users; --", # SQL injection
        ]
        return random.choice(mutations)
    
    def mutate_for_mongodb(self, field_value):
        """Apply MongoDB-specific mutations"""
        mutations = [
            '{"$ne": null}',              # Not equals null
            '{"$gt": ""}',                # Greater than empty
            '{"$regex": ".*"}',           # Regex match all
            '{"$where": "1==1"}',         # JavaScript execution
            '{"$exists": true}',          # Field exists
            '{"$in": ["admin", "user"]}', # In array
            '{"$lt": "zzzz"}',           # Less than high value
            '',                           # Empty value
            'a' * 1000,                  # Buffer overflow
            field_value + '\x00',        # Null byte injection
        ]
        return random.choice(mutations)
    
    def run_mutation_tests(self, valid_cases=None):
        """Run comprehensive mutation testing"""
        results = {
            'total_tests': 0,
            'vulnerabilities': [],
            'errors': [],
            'rate_limited': 0
        }
        
        valid_cases = valid_cases or self.generate_valid_baseline(50)
        
        for i, case in enumerate(valid_cases):
            # Test email mutations
            mutated_case = case.copy()
            mutated_case['email'] = self.mutate_email(case['email'])
            self.test_mutation(mutated_case, f"email_mutation_{i}", results)
            
            # Test password mutations
            mutated_case = case.copy()
            mutated_case['password'] = self.mutate_password(case['password'])
            self.test_mutation(mutated_case, f"password_mutation_{i}", results)
            
            # Test MongoDB-specific mutations
            mutated_case = case.copy()
            mutated_case['email'] = self.mutate_for_mongodb(case['email'])
            self.test_mutation(mutated_case, f"mongodb_email_mutation_{i}", results)
            
            mutated_case = case.copy()
            mutated_case['password'] = self.mutate_for_mongodb(case['password'])
            self.test_mutation(mutated_case, f"mongodb_password_mutation_{i}", results)
        return results
    
    def test_mutation(self, case, test_name, results):
        """Test a single mutation"""
        try:
            response = requests.post(f"{self.base_url}/login", json=case, timeout=5)
            results['total_tests'] += 1
            
            # Check for concerning responses
            if response.status_code == 200:
                results['vulnerabilities'].append({
                    'test': test_name,
                    'input': case,
                    'concern': 'Unexpected success with malformed input'
                })
            elif response.status_code == 500:
                results['errors'].append({
                    'test': test_name,
                    'input': case,
                    'error': 'Server error - potential crash'
                })
            elif response.status_code == 429:
                results['rate_limited'] += 1
                
        except Exception as e:
            results['errors'].append({
                'test': test_name,
                'input': case,
                'error': str(e)
            })
            
if __name__ == "__main__":
    tester = LoginMutationTester(base_url="http://localhost:8080")
    results = tester.run_mutation_tests()
    
    print(f"Total tests run: {results['total_tests']}")
    print(f"Vulnerabilities found: {len(results['vulnerabilities'])}")
    for vuln in results['vulnerabilities']:
        print(f"  - {vuln['test']}: {vuln['concern']} with input {vuln['input']}")
    
    print(f"Errors encountered: {len(results['errors'])}")
    for error in results['errors']:
        print(f"  - {error['test']}: {error['error']} with input {error['input']}")
    
    print(f"Rate limited responses: {results['rate_limited']}")
    
    if results['rate_limited'] > 0:
        print("Warning: Some tests were rate limited, consider adjusting the test frequency.")
        print("This may affect the completeness of the mutation testing results.")
    else:
        print("All tests completed without rate limiting issues.")
        