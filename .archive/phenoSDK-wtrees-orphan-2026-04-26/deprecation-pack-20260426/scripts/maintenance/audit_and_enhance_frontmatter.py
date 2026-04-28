#!/usr/bin/env python3
"""
Phase 4A: Frontmatter Audit & Enhancement Script
Complete metadata for all documentation files to achieve 100/100 excellence
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class FrontmatterIssue:
    file: str
    missing: List[str]
    length_issues: List[str]
    suggestions: List[str]

class FrontmatterAuditor:
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.issues: List[FrontmatterIssue] = []
        self.files_audited = 0
        self.files_with_issues = 0

    def audit_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """Audit single file frontmatter."""
        content = filepath.read_text(encoding='utf-8')
        issues = []

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            issues.append("❌ No frontmatter found")
            return False, issues

        frontmatter = match.group(1)

        # Check required fields
        required_fields = ['title', 'description', 'keywords', 'categories']
        for field in required_fields:
            if f'{field}:' not in frontmatter:
                issues.append(f"❌ Missing {field}")

        # Validate description length (150-160 chars optimal)
        desc_match = re.search(r'description:\s*["\'](.+?)["\']', frontmatter)
        if desc_match:
            desc_len = len(desc_match.group(1))
            if desc_len < 120:
                issues.append(f"⚠️  Description too short ({desc_len} chars, target 150-160)")
            elif desc_len > 160:
                issues.append(f"⚠️  Description too long ({desc_len} chars, target 150-160)")

        # Validate keywords count (3-5 minimum)
        kw_match = re.search(r'keywords:\s*\[(.*?)\]', frontmatter)
        if kw_match:
            keywords = [k.strip().strip('"\'') for k in kw_match.group(1).split(',') if k.strip()]
            if len(keywords) < 3:
                issues.append(f"⚠️  Too few keywords ({len(keywords)}, target 3-5)")
            elif len(keywords) > 7:
                issues.append(f"⚠️  Too many keywords ({len(keywords)}, target 3-5)")

        # Check for optional but recommended fields
        has_related = 'relatedPages:' in frontmatter
        has_difficulty = 'difficulty:' in frontmatter
        has_time = 'timeToRead:' in frontmatter or 'estCompletion:' in frontmatter

        # Tutorials should have difficulty and time
        if 'tutorials' in str(filepath):
            if not has_difficulty:
                issues.append("⚠️  Missing difficulty level (required for tutorials)")
            if not has_time:
                issues.append("⚠️  Missing time estimate (required for tutorials)")

        return len(issues) == 0, issues

    def run_audit(self) -> Dict:
        """Run full audit on all MDX files."""
        mdx_files = list(self.docs_dir.rglob("*.mdx"))
        issues_found = {}

        print(f"\n🔍 Auditing {len(mdx_files)} MDX files...")

        for i, mdx_file in enumerate(mdx_files, 1):
            if mdx_file.name == "index.mdx":
                continue

            self.files_audited += 1
            is_ok, file_issues = self.audit_file(mdx_file)

            if not is_ok:
                self.files_with_issues += 1
                rel_path = mdx_file.relative_to(self.docs_dir)
                issues_found[str(rel_path)] = file_issues

            if i % 50 == 0:
                print(f"  Progress: {i}/{len(mdx_files)}")

        return issues_found

    def generate_report(self, issues: Dict) -> str:
        """Generate audit report."""
        report = []
        report.append("\n" + "="*80)
        report.append("PHASE 4A: FRONTMATTER AUDIT REPORT")
        report.append("="*80)

        report.append(f"\n📊 SUMMARY")
        report.append(f"  Total files audited: {self.files_audited}")
        report.append(f"  Files with issues: {self.files_with_issues}")
        report.append(f"  Compliance rate: {100 * (1 - self.files_with_issues/max(1, self.files_audited)):.1f}%")

        if issues:
            report.append(f"\n⚠️  FILES REQUIRING ATTENTION ({len(issues)})")
            report.append("-" * 80)

            for filepath in sorted(issues.keys()):
                report.append(f"\n📄 {filepath}")
                for issue in issues[filepath]:
                    report.append(f"   {issue}")
        else:
            report.append(f"\n✅ ALL FILES COMPLIANT!")

        report.append("\n" + "="*80)
        return "\n".join(report)

class FrontmatterEnhancer:
    """Enhance frontmatter with missing or incomplete metadata."""

    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir

    def infer_metadata(self, filepath: Path) -> Dict[str, any]:
        """Infer metadata from file path and content."""
        rel_path = filepath.relative_to(self.docs_dir)
        parts = rel_path.parts

        metadata = {}

        # Infer category from path
        if 'security' in parts:
            metadata['categories'] = ['Security', 'Enterprise']
        elif 'tutorials' in parts:
            metadata['categories'] = ['Tutorials', 'Getting Started']
            metadata['difficulty'] = 'Beginner'
            metadata['timeToRead'] = 30
        elif 'architecture' in parts:
            metadata['categories'] = ['Architecture', 'Advanced']
            metadata['difficulty'] = 'Advanced'
        elif 'guides' in parts:
            metadata['categories'] = ['Guides', 'Reference']
        elif 'deployment' in parts:
            metadata['categories'] = ['Deployment', 'DevOps']
        elif 'testing' in parts:
            metadata['categories'] = ['Testing', 'Quality']
        else:
            metadata['categories'] = ['Documentation', 'Reference']

        return metadata

def main():
    docs_dir = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/apps/docs/content/docs")

    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        return

    # Run audit
    auditor = FrontmatterAuditor(docs_dir)
    issues = auditor.run_audit()

    # Generate report
    report = auditor.generate_report(issues)
    print(report)

    # Save report
    report_file = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/frontmatter_audit_report.txt")
    report_file.write_text(report)
    print(f"\n✅ Report saved to {report_file}")

    # Summary
    print(f"\n📈 AUDIT SUMMARY")
    print(f"   Files audited: {auditor.files_audited}")
    print(f"   Files compliant: {auditor.files_audited - auditor.files_with_issues}")
    print(f"   Files with issues: {auditor.files_with_issues}")
    print(f"   Compliance: {100 * (1 - auditor.files_with_issues/max(1, auditor.files_audited)):.1f}%")

if __name__ == "__main__":
    main()
