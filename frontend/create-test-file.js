// Simple script to create test files for upload testing
// Run this in the browser console or as a Node.js script

function createTestFile(filename, content) {
  const blob = new Blob([content], { type: 'text/plain' });
  const file = new File([blob], filename, { type: 'text/plain' });
  return file;
}

// Example usage:
const testContent = `This is a test document for RAGFlow.

It contains information about:
- Machine Learning
- Artificial Intelligence  
- Natural Language Processing
- Vector Databases
- Retrieval Augmented Generation

This document should be processed by the RAGFlow system and made searchable through the chat interface.`;

// Create test files
const txtFile = createTestFile('test-document.txt', testContent);
const mdFile = createTestFile('test-document.md', `# Test Document\n\n${testContent}`);

console.log('Test files created:', txtFile.name, mdFile.name);
console.log('You can now test the upload functionality with these files.');
