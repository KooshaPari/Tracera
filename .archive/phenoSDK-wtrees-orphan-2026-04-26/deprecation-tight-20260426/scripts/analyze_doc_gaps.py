#!/usr/bin/env python3
"""
Documentation Coverage Gap Analysis Script

Identifies specific gaps to reach 100% documentation coverage from 95%.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


def find_missing_module_readmes(src_path: Path) -> List[Dict]:
    """Find directories with Python files but no README.md."""
    missing_readmes = []

    # Find all directories with Python files
    dirs_with_python = set()
    for py_file in src_path.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        if '.egg-info' in str(py_file):
            continue
        dirs_with_python.add(py_file.parent)

    # Check each directory for README
    for dir_path in sorted(dirs_with_python):
        readme_path = dir_path / 'README.md'
        if not readme_path.exists():
            # Count Python files in directory
            py_files = list(dir_path.glob('*.py'))
            if py_files:
                rel_path = dir_path.relative_to(src_path.parent)
                missing_readmes.append({
                    'path': str(rel_path),
                    'python_files': len(py_files),
                    'priority': 'High' if 'domain' in str(dir_path) or 'application' in str(dir_path) else 'Medium',
                    'effort_hours': 1 if len(py_files) < 5 else 2
                })

    return missing_readmes


def find_undocumented_apis(src_path: Path) -> List[Dict]:
    """Find public functions/classes without docstrings."""
    undocumented = []

    for py_file in src_path.rglob('*.py'):
        if '__pycache__' in str(py_file) or '.egg-info' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Skip private
                    if node.name.startswith('_'):
                        continue

                    # Check docstring
                    if ast.get_docstring(node) is None:
                        node_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                        rel_path = py_file.relative_to(src_path.parent)
                        undocumented.append({
                            'file': str(rel_path),
                            'line': node.lineno,
                            'type': node_type,
                            'name': node.name,
                            'priority': 'High' if not node.name.startswith('test_') else 'Low',
                            'effort_hours': 0.25
                        })
        except Exception:
            continue

    return undocumented


def analyze_fumadocs_coverage(docs_path: Path) -> Dict:
    """Analyze fumadocs content coverage."""
    analysis = {
        'guides': {'count': 0, 'needed': []},
        'tutorials': {'count': 0, 'needed': []},
        'examples': {'count': 0, 'needed': []},
        'api_reference': {'count': 0, 'needed': []}
    }

    # Count existing
    guides_dir = docs_path / 'guides'
    if guides_dir.exists():
        analysis['guides']['count'] = len(list(guides_dir.glob('*.md*')))

    tutorials_dir = docs_path / 'tutorials'
    if tutorials_dir.exists():
        analysis['tutorials']['count'] = len(list(tutorials_dir.glob('*.md*')))

    examples_dir = docs_path / 'examples'
    if examples_dir.exists():
        analysis['examples']['count'] = len(list(examples_dir.glob('*.md*')))

    # Identify missing guides
    needed_guides = [
        {'name': 'Advanced Testing Strategies', 'priority': 'High', 'effort_hours': 6},
        {'name': 'Production Deployment Checklist', 'priority': 'High', 'effort_hours': 4},
        {'name': 'Monitoring and Observability', 'priority': 'High', 'effort_hours': 5},
        {'name': 'Security Best Practices', 'priority': 'High', 'effort_hours': 5},
        {'name': 'Performance Optimization', 'priority': 'Medium', 'effort_hours': 6},
        {'name': 'Multi-Region Deployment', 'priority': 'Medium', 'effort_hours': 4},
        {'name': 'Troubleshooting Guide', 'priority': 'Medium', 'effort_hours': 4},
    ]
    analysis['guides']['needed'] = needed_guides

    # Identify missing tutorials
    needed_tutorials = [
        {'name': 'Building a Chat Application', 'priority': 'High', 'effort_hours': 8},
        {'name': 'Implementing Authentication', 'priority': 'High', 'effort_hours': 6},
        {'name': 'Creating Custom MCP Tools', 'priority': 'Medium', 'effort_hours': 5},
        {'name': 'Database Migration Tutorial', 'priority': 'Medium', 'effort_hours': 4},
        {'name': 'Testing Your Application', 'priority': 'Medium', 'effort_hours': 5},
    ]
    analysis['tutorials']['needed'] = needed_tutorials

    # Identify missing examples
    needed_examples = [
        {'name': 'Webhook Handler', 'priority': 'Medium', 'effort_hours': 2},
        {'name': 'Background Job Processor', 'priority': 'Medium', 'effort_hours': 3},
        {'name': 'API Gateway Integration', 'priority': 'Medium', 'effort_hours': 3},
        {'name': 'Real-time Notifications', 'priority': 'Low', 'effort_hours': 4},
    ]
    analysis['examples']['needed'] = needed_examples

    return analysis


def main():
    """Run gap analysis and generate report."""
    base_path = Path(__file__).parent.parent
    src_path = base_path / 'src'
    docs_path = base_path / 'apps' / 'docs' / 'content' / 'docs'

    print("=" * 80)
    print("DOCUMENTATION COVERAGE GAP ANALYSIS")
    print("=" * 80)
    print()

    # 1. Missing Module READMEs
    print("1. Analyzing missing module READMEs...")
    missing_readmes = find_missing_module_readmes(src_path)
    print(f"   Found: {len(missing_readmes)} directories without README.md")

    # 2. Undocumented APIs
    print("2. Analyzing undocumented public APIs...")
    undocumented_apis = find_undocumented_apis(src_path)
    print(f"   Found: {len(undocumented_apis)} undocumented public APIs")

    # 3. Fumadocs content gaps
    print("3. Analyzing fumadocs content coverage...")
    fumadocs_analysis = analyze_fumadocs_coverage(docs_path)

    # Calculate totals
    total_readme_hours = sum(r['effort_hours'] for r in missing_readmes)
    total_api_hours = sum(a['effort_hours'] for a in undocumented_apis)
    total_guide_hours = sum(g['effort_hours'] for g in fumadocs_analysis['guides']['needed'])
    total_tutorial_hours = sum(t['effort_hours'] for t in fumadocs_analysis['tutorials']['needed'])
    total_example_hours = sum(e['effort_hours'] for e in fumadocs_analysis['examples']['needed'])

    total_hours = (total_readme_hours + total_api_hours + total_guide_hours +
                   total_tutorial_hours + total_example_hours)

    # Generate summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Missing Module READMEs:       {len(missing_readmes):4d} ({total_readme_hours:.1f}h)")
    print(f"Undocumented Public APIs:     {len(undocumented_apis):4d} ({total_api_hours:.1f}h)")
    print(f"Missing User Guides:          {len(fumadocs_analysis['guides']['needed']):4d} ({total_guide_hours:.1f}h)")
    print(f"Missing Tutorials:            {len(fumadocs_analysis['tutorials']['needed']):4d} ({total_tutorial_hours:.1f}h)")
    print(f"Missing Examples:             {len(fumadocs_analysis['examples']['needed']):4d} ({total_example_hours:.1f}h)")
    print("-" * 80)
    print(f"TOTAL EFFORT:                      {total_hours:.1f} hours")
    print(f"TIMELINE (40h/week):               {total_hours/40:.1f} weeks")
    print()

    # Save detailed results
    results = {
        'summary': {
            'total_items': (len(missing_readmes) + len(undocumented_apis) +
                          len(fumadocs_analysis['guides']['needed']) +
                          len(fumadocs_analysis['tutorials']['needed']) +
                          len(fumadocs_analysis['examples']['needed'])),
            'total_hours': total_hours,
            'timeline_weeks': total_hours / 40
        },
        'missing_readmes': missing_readmes,
        'undocumented_apis': undocumented_apis[:100],  # Top 100
        'fumadocs': fumadocs_analysis
    }

    output_file = base_path / 'docs' / 'audits' / 'documentation_gaps_detailed.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Detailed results saved to: {output_file}")
    print()

    # Print top priorities
    print("=" * 80)
    print("TOP 10 HIGHEST PRIORITY ITEMS")
    print("=" * 80)
    print()

    # Combine all items with priority
    all_items = []

    for readme in missing_readmes[:5]:
        if readme['priority'] == 'High':
            all_items.append({
                'type': 'Module README',
                'description': f"Create README for {readme['path']}",
                'priority': 'High',
                'effort': f"{readme['effort_hours']}h"
            })

    for guide in fumadocs_analysis['guides']['needed'][:5]:
        if guide['priority'] == 'High':
            all_items.append({
                'type': 'User Guide',
                'description': guide['name'],
                'priority': 'High',
                'effort': f"{guide['effort_hours']}h"
            })

    for tutorial in fumadocs_analysis['tutorials']['needed'][:3]:
        if tutorial['priority'] == 'High':
            all_items.append({
                'type': 'Tutorial',
                'description': tutorial['name'],
                'priority': 'High',
                'effort': f"{tutorial['effort_hours']}h"
            })

    # Add critical API docs
    api_by_file = defaultdict(list)
    for api in undocumented_apis:
        if api['priority'] == 'High':
            api_by_file[api['file']].append(api)

    for file_path, apis in sorted(api_by_file.items(), key=lambda x: len(x[1]), reverse=True)[:3]:
        all_items.append({
            'type': 'API Docstrings',
            'description': f"Document {len(apis)} APIs in {file_path}",
            'priority': 'High',
            'effort': f"{len(apis) * 0.25:.1f}h"
        })

    for i, item in enumerate(all_items[:10], 1):
        print(f"{i:2d}. [{item['priority']:6s}] {item['type']:20s} - {item['description']} ({item['effort']})")

    print()


if __name__ == '__main__':
    main()
