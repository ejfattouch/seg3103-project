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
            'no-unused-vars': 'error', // Variable declaration syntax
            'no-undef': 'error', // undefined variables
            'no-unreachable': 'error', // Control flow syntax
            semi: ['error', 'always'], // Statement termination
            quotes: ['error', 'single'], // String literal syntax
            indent: ['error', 2] // indentation structure validation
          }
        }
      ]
    });

    // Valid JavaScript patterns (ground strings from ECMAScript grammar)
    this.validPatterns = [
      'const x = 5;', // VariableStatement
      'function test() { return true; }', // FunctionDeclaration
      'if (x > 0) { console.log("positive"); }', // IfStatement
      'const obj = { key: "value" };', // ObjectLiteral
      'for (let i = 0; i < 10; i++) { }' // IterationStatement
    ];

    // Invalid mutations (should fail)
    this.invalidMutations = [
      'const = 5;', // Missing identifier
      'function () { return true; }', // Missing function name
      'if x > 0) { console.log("positive"); }', // Missing opening paren
      'const obj = { key "value" };', // Missing colon
      'for let i = 0; i < 10; i++) { }' // Missing opening paren
    ];
  }

  async testValidPatterns() {
    console.log('=== Testing Valid JavaScript Grammar Patterns ===\n');
    let passCount = 0;

    for (const pattern of this.validPatterns) {
      try {
        const results = await this.eslint.lintText(pattern);
        const hasParseErrors = results[0].messages.some((msg) => msg.severity === 2 && msg.fatal);

        if (!hasParseErrors) {
          console.log(`✓ VALID: ${pattern}`);
          passCount++;
        } else {
          console.log(`✗ FAILED: ${pattern}`);
          // Show the actual error
          results[0].messages.forEach((msg) => {
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

  async testInvalidMutations() {
    console.log('=== Testing Invalid Grammar Mutations ===\n');
    let rejectCount = 0;

    for (const mutation of this.invalidMutations) {
      try {
        const results = await this.eslint.lintText(mutation);
        const hasParseErrors = results[0].messages.some((msg) => msg.severity === 2 && msg.fatal);

        if (hasParseErrors) {
          console.log(`✓ CORRECTLY REJECTED: ${mutation}`);
          rejectCount++;
        } else {
          console.log(`✗ SHOULD HAVE FAILED: ${mutation}`);
        }
      } catch (error) {
        console.log(`✓ CORRECTLY REJECTED: ${mutation} - Parse Error`);
        rejectCount++;
      }
    }

    console.log(`\nInvalid Mutations: ${rejectCount}/${this.invalidMutations.length} correctly rejected\n`);
    return rejectCount;
  }

  async testCodebaseFiles() {
    console.log('=== Testing Real Codebase Files ===\n');

    const targetFiles = ['./controllers/ai.js', './app.js']; // Check both locations

    for (const file of targetFiles) {
      if (fs.existsSync(file)) {
        try {
          const results = await this.eslint.lintFiles([file]);
          const result = results[0];

          console.log(`File: ${file}`);
          console.log(`  Total Issues: ${result.messages.length}`);
          console.log(`  Errors: ${result.errorCount}`);
          console.log(`  Warnings: ${result.warningCount}`);

          if (result.messages.length > 0) {
            console.log('  Sample Issues:');
            result.messages.slice(0, 5).forEach((msg) => {
              console.log(`    Line ${msg.line}: ${msg.message} (${msg.ruleId || 'parse-error'})`);
            });
          }
        } catch (error) {
          console.log(`  ✗ File has syntax errors: ${error.message}`);
        }
      } else {
        console.log(`  ✗ File not found: ${file}`);
      }
    }
    console.log('');
  }

  async runAllTests() {
    console.log('ESLint-Based Syntax Testing Framework\n');
    console.log('=====================================\n');

    const validCount = await this.testValidPatterns();
    const rejectCount = await this.testInvalidMutations();
    await this.testCodebaseFiles();

    console.log('=== SUMMARY ===');
    console.log(`Valid patterns accepted: ${validCount}/${this.validPatterns.length}`);
    console.log(`Invalid mutations rejected: ${rejectCount}/${this.invalidMutations.length}`);

    return {
      validPassed: validCount,
      invalidRejected: rejectCount,
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
