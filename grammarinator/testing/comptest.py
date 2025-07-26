import json
from mutation_tester import LoginMutationTester
from property_tester import PropertyBasedTester
from security_tester import SecurityTester


def run_comprehensive_tests():
    print("=== Grammar-Based Testing Demonstration ===\n")
    
    # 1. Baseline Generation
    print("1. Generating baseline valid inputs...")
    mutation_tester = LoginMutationTester()
    valid_cases = mutation_tester.generate_valid_baseline(50)
    print(f"Generated {len(valid_cases)} valid test cases")
    
   # 2. Security Grammar Testing
    print("\n2. Running security grammar tests...")
    security_tester = SecurityTester()
    security_results = security_tester.run_security_grammar_tests()
    print(f"Security grammar testing completed:")
    print(f"  - Total security tests: {security_results['total_tests']}")
    print(f"  - Attack patterns tested: {security_results['attack_patterns']}")
    print(f"  - Successful attacks: {len(security_results['successful_attacks'])}")
    
    # 3. Mutation Testing
    print("\n2. Running mutation tests...")
    mutation_results = mutation_tester.run_mutation_tests(valid_cases=valid_cases)
    print(f"Mutation testing completed:")
    print(f"  - Total tests: {mutation_results['total_tests']}")
    print(f"  - Vulnerabilities found: {len(mutation_results['vulnerabilities'])}")
    print(f"  - Errors found: {len(mutation_results['errors'])}")
    print(f"  - Rate limited: {mutation_results['rate_limited']}")
    
    # 4. Property-Based Testing
    print("\n3. Running property-based tests...")
    property_tester = PropertyBasedTester()
    try:
        property_tester.test_login_properties()
        print("  ✅ All properties maintained")
    except AssertionError as e:
        print(f"  ❌ Property violation: {e}")
    
    # 5. Generate Comprehensive Report
    print("\n5. Comprehensive Test Summary:")
    print("="*60)
    print("SECURITY GRAMMAR RESULTS:")
    for attack in security_results['successful_attacks']:
        print(f"🔴 ATTACK SUCCEEDED: {attack['type']}")
        print(f"   Input: {attack['input']}")
        
    if security_results['successful_attacks'] == []:
        print("✅ No security vulnerabilities found in security grammar testing.")
    
    print("\nMUTATION TESTING RESULTS:")
    for vuln in mutation_results['vulnerabilities']:
        print(f"🔴 VULNERABILITY: {vuln['concern']}")
        print(f"   Input: {vuln['input']}")
        
    if mutation_results['vulnerabilities'] == []:
        print("✅ No vulnerabilities found in mutation testing.")
    
    for error in mutation_results['errors'][:3]:
        print(f"🟡 ERROR: {error['error']}")
        print(f"   Input: {error['input']}")
        
    if mutation_results['errors'] == []:
        print("✅ No errors found in mutation testing.")
        
    # Summary
    total_issues = (len(security_results['successful_attacks']) + 
                   len(mutation_results['vulnerabilities']) + 
                   len(mutation_results['errors']))
    
    if total_issues > 0:
        print(f"\n⚠️  TOTAL ISSUES FOUND: {total_issues}")
        print("Please review the above issues to improve your login system's security.")
    else:
        print("\n✅ No critical issues found. Your login system appears robust against tested attacks.")

if __name__ == "__main__":
    run_comprehensive_tests()