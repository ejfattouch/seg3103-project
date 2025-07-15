const { JavaScriptGrammarTester } = require('./eslint-grammar-testing');

async function main() {
  console.log('Starting ESLint Syntax-Based Testing...\n');
  
  const tester = new JavaScriptGrammarTester();
  const results = await tester.runAllTests();
  
  console.log('\n=== TEST EXECUTION COMPLETE ===');

  if (results.error_count > 0) {
    console.error(`Syntax errors found: ${results.error_count}`);
  }

  process.exit(0);
}

main().catch((error) => {
  console.error('Test execution failed:', error);
  process.exit(1);
});

