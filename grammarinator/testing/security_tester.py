import json
import requests
import os
import sys

# Add the grammar directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'grammar'))

class SecurityTester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.attack_patterns = ['XSS', 'Buffer Overflow', 'Malformed Input', 'JSON Parser Attacks']
        
    def run_security_grammar_tests(self, num_tests=30):
        """Run tests using the security grammar"""
        results = {
            'total_tests': 0,
            'attack_patterns': self.attack_patterns,
            'successful_attacks': [],
            'json_parser_attacks': [],  # NEW: Track JSON parser attacks
            'malformed_inputs': []      # NEW: Track malformed inputs that might be dangerous
        }
        
        try:
            # Import the security grammar generator
            from SecurityTestGrammarGenerator import SecurityTestGrammarGenerator
            from grammarinator.runtime import DefaultModel
            
            security_generator = SecurityTestGrammarGenerator(model=DefaultModel())
            
            # Generate security test cases
            for i in range(num_tests):
                try:
                    # Generate malicious login attempt
                    malicious_json = security_generator.malicious_login()
                    raw_input = str(malicious_json)
                    
                    # Try to parse as JSON first
                    try:
                        test_case = json.loads(raw_input)
                        # If it parses, test it normally
                        self._test_valid_json(test_case, f"valid_json_{i}", results)
                        
                    except json.JSONDecodeError as json_err:
                        # This is where the potential threats are!
                        # Test the raw malformed input directly
                        self._test_malformed_input(raw_input, f"malformed_json_{i}", results, json_err)
                        
                except Exception as e:
                    # Log generator errors
                    results['successful_attacks'].append({
                        'type': 'Generator Error',
                        'input': f"Generator failed: {str(e)}",
                        'response': 'N/A'
                    })
                    
        except ImportError:
            print("⚠️  SecurityTestGrammarGenerator not found. Run: grammarinator-process securityTest.g4 -o ../grammar/")
            results['total_tests'] = 0
        
        return results
    
    def _test_valid_json(self, test_case, test_name, results):
        """Test valid JSON inputs"""
        try:
            response = requests.post(f"{self.base_url}/login", json=test_case, timeout=5)
            results['total_tests'] += 1
            
            # Check for concerning responses
            if response.status_code == 200:
                results['successful_attacks'].append({
                    'type': 'Authentication Bypass',
                    'input': test_case,
                    'response': response.status_code,
                    'test_name': test_name
                })
            elif response.status_code == 500:
                results['successful_attacks'].append({
                    'type': 'Server Error (Potential Crash)',
                    'input': test_case,
                    'response': response.status_code,
                    'test_name': test_name
                })
                
        except Exception as e:
            results['successful_attacks'].append({
                'type': 'Valid JSON Request Error',
                'input': test_case,
                'error': str(e),
                'test_name': test_name
            })
    
    def _test_malformed_input(self, raw_input, test_name, results, json_error):
        """Test malformed JSON inputs - these could be the most dangerous!"""
        results['malformed_inputs'].append({
            'input': raw_input,
            'json_error': str(json_error),
            'test_name': test_name
        })
        
        try:
            # Send raw malformed data as the request body
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{self.base_url}/login", data=raw_input, headers=headers, timeout=5)
            results['total_tests'] += 1
            
            # ANY response to malformed JSON could be concerning
            if response.status_code == 200:
                results['json_parser_attacks'].append({
                    'type': 'JSON Parser Bypass - Authentication Success',
                    'input': raw_input,
                    'response': response.status_code,
                    'concern': 'Server accepted malformed JSON and authenticated!',
                    'test_name': test_name
                })
            elif response.status_code == 500:
                results['json_parser_attacks'].append({
                    'type': 'JSON Parser Crash',
                    'input': raw_input,
                    'response': response.status_code,
                    'concern': 'Malformed JSON caused server error - potential DoS',
                    'test_name': test_name
                })
            elif response.status_code not in [400, 422]:  # Expected error codes for bad JSON
                results['json_parser_attacks'].append({
                    'type': 'Unexpected JSON Parser Response',
                    'input': raw_input,
                    'response': response.status_code,
                    'concern': f'Unexpected response code {response.status_code} for malformed JSON',
                    'test_name': test_name
                })
                
        except requests.exceptions.RequestException as e:
            # Network errors with malformed input - could indicate parsing issues
            results['json_parser_attacks'].append({
                'type': 'Network Error with Malformed Input',
                'input': raw_input,
                'error': str(e),
                'concern': 'Malformed input caused network-level error',
                'test_name': test_name
            })
        except Exception as e:
            results['json_parser_attacks'].append({
                'type': 'Malformed Input Processing Error',
                'input': raw_input,
                'error': str(e),
                'test_name': test_name
            })
    
    def print_security_results(self, results):
        """Print formatted security test results"""
        print("=== Security Grammar Testing Results ===")
        print(f"Total security tests: {results['total_tests']}")
        print(f"Attack patterns tested: {results['attack_patterns']}")
        print(f"Successful attacks: {len(results['successful_attacks'])}")
        print(f"JSON parser attacks: {len(results['json_parser_attacks'])}")
        print(f"Malformed inputs tested: {len(results['malformed_inputs'])}")
        
        # Regular attacks
        if results['successful_attacks']:
            print("\n🔍 REGULAR SECURITY VULNERABILITIES:")
            for attack in results['successful_attacks']:
                print(f"🔴 ATTACK SUCCEEDED: {attack['type']}")
                print(f"   Input: {attack['input']}")
                print(f"   Response: {attack.get('response', 'N/A')}")
        
        # JSON parser attacks (the ones we were missing!)
        if results['json_parser_attacks']:
            print("\n🚨 JSON PARSER ATTACKS (CRITICAL):")
            for attack in results['json_parser_attacks']:
                print(f"🔥 CRITICAL: {attack['type']}")
                print(f"   Input: {attack['input'][:100]}...")  # Truncate long inputs
                print(f"   Response: {attack.get('response', 'N/A')}")
                print(f"   Concern: {attack.get('concern', 'Malformed input processed')}")
        
        # Summary
        total_issues = len(results['successful_attacks']) + len(results['json_parser_attacks'])
        if total_issues == 0:
            print("\n✅ No security vulnerabilities found in grammar-based testing.")
        else:
            print(f"\n⚠️  TOTAL SECURITY ISSUES: {total_issues}")
            if results['json_parser_attacks']:
                print("🚨 CRITICAL: JSON parser vulnerabilities found - these are often the most dangerous!")

if __name__ == "__main__":
    tester = SecurityTester(base_url="http://localhost:8080")
    results = tester.run_security_grammar_tests(100)
    tester.print_security_results(results)