const fs = require('fs');
const path = require('path');

const DOCS_STRUCTURE = {
  'getting-started': {
    title: 'Getting Started',
    path: '00-getting-started',
    children: {
      'installation': { title: 'Installation', path: '01-installation' },
      'quick-start': { title: 'Quick Start', path: '02-quick-start' },
      'system-requirements': { title: 'System Requirements', path: '03-system-requirements' },
      'core-concepts': { title: 'Core Concepts', path: '04-core-concepts' },
      'first-project': { title: 'First Project', path: '05-first-project' },
      'basic-workflow': { title: 'Basic Workflow', path: '06-basic-workflow' },
      'faq': { title: 'FAQ', path: '07-faq' },
    },
  },
};

function createMdxFile(dirPath, title) {
  const mdxContent = `---
title: "${title}"
description: "Documentation for ${title}"
---

# ${title}

This page contains documentation for ${title}.

## Overview

This section covers the key aspects of ${title} in TraceRTM.

## Getting Started

To get started with ${title}:

- Review the ${title} and fundamentals
- Explore practical examples
- Check out the API reference

## Key Concepts

- **Concept 1**: Description of concept 1
- **Concept 2**: Description of concept 2
- **Concept 3**: Description of concept 3

## Next Steps

- [Learn more about related topics](#)
- [View examples](#)
- [Check the API reference](#)
`;

  fs.mkdirSync(dirPath, { recursive: true });
  fs.writeFileSync(path.join(dirPath, 'index.mdx'), mdxContent);
}

function generateDocs(items, basePath = '') {
  Object.entries(items).forEach(([key, value]) => {
    const dirPath = path.join(basePath, value.path);
    createMdxFile(dirPath, value.title);
    console.log(`✓ Created ${dirPath}/index.mdx`);
    
    if (value.children) {
      generateDocs(value.children, dirPath);
    }
  });
}

const docsPath = path.join(__dirname, 'content', 'docs');
generateDocs(DOCS_STRUCTURE, docsPath);
console.log('\n✅ All documentation files generated!');

