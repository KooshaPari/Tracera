#!/usr/bin/env python3
"""Comprehensive library usage audit."""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict
import subprocess

# Key libraries to audit
KEY_LIBRARIES = {
    'aiocache': ['aiocache', 'Cache', 'SimpleMemoryCache'],
    'httpx': ['httpx', 'AsyncClient', 'Client'],
    'tenacity': ['tenacity', 'retry', 'stop_after_attempt'],
    'prometheus_client': ['prometheus_client', 'Counter', 'Gauge', 'Histogram'],
    'opentelemetry': ['opentelemetry', 'trace', 'metrics'],
    'structlog': ['structlog', 'get_logger'],
    'pydantic': ['pydantic', 'BaseModel', 'Field', 'validator'],
    'cattrs': ['cattrs', 'structure', 'unstructure'],
    'attrs': ['attrs', 'attr', 'define'],
    'msgspec': ['msgspec', 'Struct'],
    'polars': ['polars', 'DataFrame'],
    'orjson': ['orjson', 'dumps', 'loads'],
    'asyncpg': ['asyncpg', 'create_pool'],
    'meilisearch': ['meilisearch', 'Client'],
    'valkey': ['valkey', 'Valkey'],
    'duckdb': ['duckdb', 'connect'],
}

# Custom implementation patterns to find
CUSTOM_PATTERNS = {
    'cache': [
        r'class\s+\w*Cache\w*\(',
        r'def\s+cache_\w+\(',
        r'@cache',
        r'_cache\s*=\s*\{',
    ],
    'http_client': [
        r'class\s+\w*HTTP\w*Client\w*\(',
        r'class\s+\w*HttpClient\w*\(',
        r'def\s+http_\w+\(',
        r'requests\.',
        r'urllib\.',
    ],
    'retry': [
        r'class\s+\w*Retry\w*\(',
        r'def\s+retry_\w+\(',
        r'@retry',
        r'for\s+\w+\s+in\s+range\(\w*retry',
    ],
    'metrics': [
        r'class\s+\w*Metrics?\w*\(',
        r'class\s+\w*Counter\w*\(',
        r'def\s+increment_\w+\(',
        r'def\s+record_\w+\(',
    ],
    'serialization': [
        r'def\s+to_dict\(',
        r'def\s+from_dict\(',
        r'def\s+serialize\(',
        r'def\s+deserialize\(',
        r'json\.dumps',
        r'json\.loads',
    ],
    'validation': [
        r'class\s+\w*Validator\w*\(',
        r'def\s+validate_\w+\(',
        r'if\s+not\s+isinstance\(',
    ],
}

def find_imports(src_dir):
    """Find all imports in the codebase."""
    imports = defaultdict(list)
    
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find import statements
                import_pattern = r'^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))'
                for match in re.finditer(import_pattern, content, re.MULTILINE):
                    module = match.group(1) or match.group(2)
                    base_module = module.split('.')[0]
                    imports[base_module].append(filepath)
            except:
                pass
    
    return imports

def find_custom_implementations(src_dir):
    """Find custom implementations that might duplicate library functionality."""
    findings = defaultdict(list)
    
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if not file.endswith('.py'):
                continue
                
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for category, patterns in CUSTOM_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            findings[category].append(filepath)
                            break
            except:
                pass
    
    return findings

def count_loc(filepath):
    """Count lines of code in a file."""
    try:
        result = subprocess.run(['wc', '-l', filepath], capture_output=True, text=True)
        return int(result.stdout.split()[0])
    except:
        return 0

def main():
    src_dir = 'src'
    
    print("=" * 80)
    print("COMPREHENSIVE LIBRARY USAGE AUDIT")
    print("=" * 80)
    print()
    
    # Find all imports
    print("Step 1: Analyzing imports...")
    imports = find_imports(src_dir)
    
    print("\nKEY LIBRARY USAGE:")
    print("-" * 80)
    
    for lib, keywords in KEY_LIBRARIES.items():
        base_lib = lib.split('_')[0]
        if base_lib in imports:
            files = set(imports[base_lib])
            print(f"\n✅ {lib}: {len(files)} files")
            if len(files) <= 5:
                for f in sorted(files)[:5]:
                    print(f"   - {f}")
        else:
            print(f"\n❌ {lib}: NOT USED (but may be installed)")
    
    # Find custom implementations
    print("\n" + "=" * 80)
    print("Step 2: Finding custom implementations...")
    print("=" * 80)
    
    custom = find_custom_implementations(src_dir)
    
    total_custom_loc = 0
    for category, files in sorted(custom.items()):
        unique_files = set(files)
        loc = sum(count_loc(f) for f in unique_files)
        total_custom_loc += loc
        
        print(f"\n{category.upper()}: {len(unique_files)} files, ~{loc} LOC")
        for f in sorted(unique_files)[:5]:
            file_loc = count_loc(f)
            print(f"   - {f} ({file_loc} LOC)")
        if len(unique_files) > 5:
            print(f"   ... and {len(unique_files) - 5} more files")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal custom implementation LOC: ~{total_custom_loc}")
    print(f"Categories with custom code: {len(custom)}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    recommendations = []
    
    if 'cache' in custom and 'aiocache' not in imports:
        recommendations.append(("HIGH", "Replace custom cache with aiocache", len(custom['cache'])))
    
    if 'http_client' in custom and 'httpx' not in imports:
        recommendations.append(("HIGH", "Replace custom HTTP clients with httpx", len(custom['http_client'])))
    
    if 'retry' in custom and 'tenacity' not in imports:
        recommendations.append(("HIGH", "Replace custom retry logic with tenacity", len(custom['retry'])))
    
    if 'metrics' in custom and 'prometheus_client' not in imports:
        recommendations.append(("HIGH", "Replace custom metrics with prometheus_client", len(custom['metrics'])))
    
    if 'serialization' in custom:
        if 'cattrs' not in imports and 'msgspec' not in imports:
            recommendations.append(("MEDIUM", "Replace custom serialization with cattrs/msgspec", len(custom['serialization'])))
    
    if 'validation' in custom and 'pydantic' not in imports:
        recommendations.append(("MEDIUM", "Replace custom validation with pydantic", len(custom['validation'])))
    
    for priority, rec, file_count in sorted(recommendations, key=lambda x: (x[0], -x[2])):
        print(f"\n{priority}: {rec}")
        print(f"   Affects {file_count} files")
    
    if not recommendations:
        print("\n✅ No major issues found! Most custom code already replaced.")

if __name__ == "__main__":
    main()

