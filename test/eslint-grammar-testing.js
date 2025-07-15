const { ESLint } = require('eslint');
const fs = require('fs');
const path = require('path');

class JavaScriptGrammarTester {
  constructor() {
    this.eslint = new ESLint({
      overrideConfigFile: true,
      overrideConfig: [
        {
          languageOptions: {
            ecmaVersion: 2021,
            sourceType: 'module',
            globals: {
              console: 'readonly',
              process: 'readonly',
              Buffer: 'readonly',
              __dirname: 'readonly',
              __filename: 'readonly',
              exports: 'writable',
              global: 'readonly',
              module: 'writable',
              require: 'readonly'
            }
          },
          rules: {
            // syntax rules
            'no-unused-vars': 'error',
            'no-undef': 'error',
            'no-unreachable': 'error',

            // code style conventions
            'semi': ['error', 'always'],           //  Semicolon requirement
            'camelcase': 'error',                  //  CamelCase naming
            'quotes': ['error', 'single'],         //  Single quotes only
            'indent': ['error', 2],                //  2-space indentation
            'brace-style': ['error', '1tbs'],      //  One True Brace Style
          }
        }
      ]
    });

    // Valid JavaScript patterns and conventions
    this.validPatterns = [
      'const x = 5;',
      'function test() { return true; }',
      'if (x > 0) { console.log("positive"); }',
      'const obj = { key: "value" };',
      'for (let i = 0; i < 10; i++) { }',
      'const userName = "john";'              // camelCase naming
    ];

    // Invalid mutations (should fail)
    this.invalidMutations = [
      // Convention violations
      'const user_name = "john";',             // camelCase violation (snake_case)
      'const x = 5',                           // Missing semicolon
      'const str = "double quotes";',          // Should use single quotes
      'if (true) {\nconsole.log("bad");\n}',   // Wrong indentation
      'if (true)\n{\n  console.log("test");\n}', // Wrong brace style

      // Syntax errors (parse failures)
      'function () { return true; }',          // Missing function name
      'if x > 0) { console.log("positive"); }', // Missing opening paren
      'const obj = { key "value" };',          // Missing colon
      'for let i = 0; i < 10; i++) { }',      // Missing opening parenthesis
      'const = 5;'                             // Missing identifier
    ];

    // Mutation operators
    this.mutationOperators = {
      removeSemicolon: (code) => code.replace(/;/g, ''),
      wrongOperator: (code) => code.replace(/=/g, '=='),
      missingOperator: (code) => code.replace(/\s*=\s*/g, ' '),
      unbalancedQuotes: (code) => code.replace(/"([^"]*)"/g, '"$1'),
      removeReturn: (code) => code.replace(/return\s+/g, ''),
      removeFunctionName: (code) => code.replace(/function\s+\w+/g, 'function')
    };
  }

  async testValidPatterns() {
    console.log('=== Testing Valid JavaScript Grammar Patterns ===\n');
    let passCount = 0;

    for (const pattern of this.validPatterns) {
      try {
        const results = await this.eslint.lintText(pattern);
        const hasParseErrors = results[0].messages.some(msg => msg.severity === 2 && msg.fatal);

        if (!hasParseErrors) {
          console.log(`✓ VALID: ${pattern}`);
          passCount++;
        } else {
          console.log(`✗ FAILED: ${pattern}`);
          results[0].messages.forEach(msg => {
            if (msg.fatal) {
              console.log(`  Parse Error: ${msg.message}`);
            }
          });
        }
      } catch (error) {
        console.log(`✗ ERROR: ${pattern} - ${error.message}`);
      }
    }

    console.log(`\nValid Patterns: ${passCount}/${this.validPatterns.length} passed\n`);
    return passCount;
  }

  async testMutations() {
    console.log('=== Mutation Testing ===\n');

    let totalMutations = 0;
    let rejectedMutations = 0;

    for (const validPattern of this.validPatterns) {
      console.log(`Generating mutations for: ${validPattern}`);

      for (const [operatorName, mutationFn] of Object.entries(this.mutationOperators)) {
        try {
          const mutatedCode = mutationFn(validPattern);

          // Only test if the mutation actually changed the code
          if (mutatedCode !== validPattern) {
            totalMutations++;

            try {
              const results = await this.eslint.lintText(mutatedCode);
              const hasErrors = results[0].messages.some(msg => msg.severity === 2);

              if (hasErrors) {
                console.log(`  ✓ ${operatorName}: "${mutatedCode}" - CORRECTLY REJECTED`);
                rejectedMutations++;
              } else {
                console.log(`  ✗ ${operatorName}: "${mutatedCode}" - SHOULD HAVE FAILED`);
              }
            } catch (error) {
              console.log(`  ✓ ${operatorName}: "${mutatedCode}" - PARSE ERROR (correctly rejected)`);
              rejectedMutations++;
            }
          }
        } catch (error) {
          // Skip mutations that fail to generate
        }
      }
      console.log('');
    }

    console.log(`Mutation Results: ${rejectedMutations}/${totalMutations} mutations correctly rejected\n`);
    return { rejected: rejectedMutations, total: totalMutations };
  }

  async testInvalidMutations() {
    console.log('=== Testing Invalid Grammar Mutations & Convention Violations ===\n');

    let syntaxRejectCount = 0;
    let conventionViolationCount = 0;

    for (const mutation of this.invalidMutations) {
      try {
        const results = await this.eslint.lintText(mutation);
        const hasParseErrors = results[0].messages.some(msg => msg.severity === 2 && msg.fatal);
        const hasStyleViolations = results[0].messages.some(msg => msg.severity === 2 && !msg.fatal);

        if (hasParseErrors) {
          console.log(`✓ SYNTAX ERROR: ${mutation}`);
          syntaxRejectCount++;
        } else if (hasStyleViolations) {
          console.log(`✓ CONVENTION VIOLATION: ${mutation}`);
          // Show which rule was violated
          const violations = results[0].messages.filter(msg => msg.ruleId);
          violations.forEach(violation => {
            console.log(`  Rule: ${violation.ruleId}`);
          });
          conventionViolationCount++;
        } else {
          console.log(`✗ NOT DETECTED: ${mutation}`);
        }
      } catch (error) {
        console.log(`✓ PARSE ERROR: ${mutation}`);
        syntaxRejectCount++;
      }
    }

    console.log(`\nMutation Results: ${syntaxRejectCount} syntax errors, ${conventionViolationCount} convention violations detected\n`);
    return { syntaxErrors: syntaxRejectCount, conventionViolations: conventionViolationCount };
  }

  async testCodebaseFiles() {
    console.log('=== Testing Real Codebase Files ===\n');

    const targetFiles = ['app.js'];  // Check both locations

    let errorCount = 0;

    for (const file of targetFiles) {
      if (fs.existsSync(file)) {
        try {
          const results = await this.eslint.lintFiles([file]);
          const result = results[0];

          console.log(`File: ${file}`);
          console.log(`  Total Issues: ${result.messages.length}`);
          console.log(`  Errors: ${result.errorCount}`);
          console.log(`  Warnings: ${result.warningCount}`);

          errorCount += result.errorCount;

          if (result.messages.length > 0) {
            console.log('  Top Issues:');
            result.messages.slice(0, 5).forEach(msg => {
              console.log(`    Line ${msg.line}: ${msg.message} (${msg.ruleId || 'parse-error'})`);
            });
          } else {
            console.log('  ✓ No issues found!');
          }
          break;
        } catch (error) {
          console.log(`  ✗ File has syntax errors: ${error.message}`);
        }
      } else {
        console.log(`  ✗ File not found: ${file}`);
      }
    }
    console.log('');

    return {
      error_count: errorCount
    };
  }

  async runAllTests() {
    console.log('Enhanced ESLint-Based Syntax Testing Framework\n');
    console.log('==============================================\n');

    const validCount = await this.testValidPatterns();
    const mutationResults = await this.testMutations();
    const invalidResults = await this.testInvalidMutations();
    await this.testCodebaseFiles();

    console.log('=== ENHANCED SUMMARY ===');
    console.log(`Valid patterns accepted: ${validCount}/${this.validPatterns.length}`);
    console.log(`Mutations rejected: ${mutationResults.rejected}/${mutationResults.total}`);
    console.log(`Invalid mutations rejected: ${invalidResults.syntaxErrors + invalidResults.conventionViolations}/${this.invalidMutations.length}`);

    return {
      validPassed: validCount,
      MutationsRejected: mutationResults.rejected,
      totalMutations: mutationResults.total,
      syntaxErrorsDetected: invalidResults.syntaxErrors,
      conventionViolationsDetected: invalidResults.conventionViolations,
      totalValid: this.validPatterns.length,
      totalInvalid: this.invalidMutations.length
    };
  }
}

// Run the tests if this file is executed directly
if (require.main === module) {
  const tester = new JavaScriptGrammarTester();
  tester.runAllTests().catch(console.error);
}

module.exports = { JavaScriptGrammarTester };