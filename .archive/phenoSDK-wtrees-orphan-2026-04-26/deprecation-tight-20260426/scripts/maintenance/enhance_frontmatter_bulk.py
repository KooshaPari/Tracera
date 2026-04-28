#!/usr/bin/env python3
"""
Phase 4A: Bulk Frontmatter Enhancement
Auto-enhance all 399 documentation files with complete metadata
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional

CATEGORY_MAPPING = {
    'security': {
        'categories': ['Security', 'Enterprise'],
        'keywords_base': ['security', 'authentication', 'authorization'],
    },
    'tutorials': {
        'categories': ['Tutorials', 'Getting Started'],
        'keywords_base': ['tutorial', 'guide', 'step-by-step'],
        'difficulty': 'Beginner',
        'timeToRead': 30,
    },
    'architecture': {
        'categories': ['Architecture', 'Advanced'],
        'keywords_base': ['architecture', 'design', 'pattern'],
        'difficulty': 'Advanced',
    },
    'guides': {
        'categories': ['Guides', 'Reference'],
        'keywords_base': ['guide', 'how-to', 'reference'],
    },
    'deployment': {
        'categories': ['Deployment', 'DevOps'],
        'keywords_base': ['deployment', 'devops', 'production'],
    },
    'testing': {
        'categories': ['Testing', 'Quality'],
        'keywords_base': ['testing', 'quality', 'verification'],
    },
    'api': {
        'categories': ['API Reference', 'Documentation'],
        'keywords_base': ['api', 'reference', 'documentation'],
    },
}

def extract_title_from_content(content: str, filepath: Path) -> str:
    """Extract or infer title from file content."""
    # Try to extract from H1 heading
    h1_match = re.search(r'^# (.+?)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # Fallback: create title from filename
    name = filepath.stem.replace('-', ' ').replace('_', ' ').title()
    return name

def infer_description(content: str, title: str) -> str:
    """Generate description from content."""
    # Extract first paragraph or summary
    lines = content.split('\n')

    description_lines = []
    for line in lines:
        if line.startswith('#'):
            continue
        if line.strip() and not line.startswith('-'):
            description_lines.append(line.strip())
            if len(' '.join(description_lines)) > 120:
                break

    description = ' '.join(description_lines)[:160]

    # Ensure it's 150-160 chars
    if len(description) < 150:
        description = (description + f". Comprehensive guide to {title.lower()}.")[
            :160
        ]

    return description.rstrip()

def infer_keywords(filepath: Path, title: str) -> List[str]:
    """Generate contextual keywords."""
    keywords = set()

    # Add title-based keywords
    title_words = [w.lower() for w in title.split() if len(w) > 3]
    keywords.update(title_words[:3])

    # Add path-based keywords
    path_parts = filepath.parts
    for part in path_parts:
        if part not in ['docs', 'content']:
            keywords.add(part.lower())

    # Add category-specific keywords
    for category_key, category_info in CATEGORY_MAPPING.items():
        if category_key in str(filepath).lower():
            keywords.update(category_info.get('keywords_base', []))

    # Generic fallback keywords
    if not keywords:
        keywords.update(['documentation', 'guide', 'reference'])

    # Return 3-5 keywords
    return sorted(list(keywords))[:5]

def infer_categories(filepath: Path) -> List[str]:
    """Infer categories from file path."""
    path_str = str(filepath).lower()

    for category_key, category_info in CATEGORY_MAPPING.items():
        if category_key in path_str:
            return category_info['categories']

    return ['Documentation', 'Reference']

def infer_difficulty(filepath: Path) -> Optional[str]:
    """Infer difficulty level from path."""
    path_str = str(filepath).lower()

    if 'advanced' in path_str or 'architecture' in path_str:
        return 'Advanced'
    elif 'tutorial' in path_str:
        return 'Beginner'

    return None

def create_new_frontmatter(filepath: Path, content: str) -> str:
    """Create complete frontmatter for a file."""
    # Extract from content
    title = extract_title_from_content(content, filepath)
    description = infer_description(content, title)
    keywords = infer_keywords(filepath, title)
    categories = infer_categories(filepath)
    difficulty = infer_difficulty(filepath)

    # Build frontmatter
    frontmatter_lines = [
        '---',
        f'title: "{title}"',
        f'description: "{description}"',
        f'keywords: {json.dumps(keywords)}',
        f'categories: {json.dumps(categories)}',
    ]

    # Add optional fields
    if difficulty:
        frontmatter_lines.append(f'difficulty: "{difficulty}"')

    if 'tutorial' in str(filepath).lower():
        frontmatter_lines.append('timeToRead: 30')

    frontmatter_lines.append('---')

    return '\n'.join(frontmatter_lines)

def enhance_file(filepath: Path) -> bool:
    """Enhance a single file with complete frontmatter."""
    try:
        content = filepath.read_text(encoding='utf-8')

        # Remove old frontmatter if it exists
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            content = content[len(match.group(0)):]

        # Get body content
        body = content.lstrip()

        # Create new frontmatter
        new_frontmatter = create_new_frontmatter(filepath, body)

        # Combine
        enhanced_content = new_frontmatter + '\n\n' + body

        # Write back
        filepath.write_text(enhanced_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    docs_dir = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/apps/docs/content/docs")

    mdx_files = sorted(list(docs_dir.rglob("*.mdx")))
    mdx_files = [f for f in mdx_files if f.name != "index.mdx"]

    print(f"\n🚀 Enhancing {len(mdx_files)} documentation files...")
    print("="*80)

    successful = 0
    failed = 0

    for i, mdx_file in enumerate(mdx_files, 1):
        rel_path = mdx_file.relative_to(docs_dir)

        if enhance_file(mdx_file):
            successful += 1
            if i % 50 == 0 or i == 1:
                print(f"✅ {i:3d}/{len(mdx_files)} - {rel_path}")
        else:
            failed += 1
            print(f"❌ {i:3d}/{len(mdx_files)} - {rel_path}")

    print("="*80)
    print(f"\n📊 ENHANCEMENT COMPLETE")
    print(f"   Total files: {len(mdx_files)}")
    print(f"   Successfully enhanced: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {100*successful/len(mdx_files):.1f}%")

if __name__ == "__main__":
    main()
