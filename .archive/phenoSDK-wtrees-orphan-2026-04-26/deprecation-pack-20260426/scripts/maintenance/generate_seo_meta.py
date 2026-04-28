#!/usr/bin/env python3
"""
Phase 4B: SEO & Navigation Meta-Generation
Generate canonical URLs, OG tags, structured data for all documentation
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class SEOMetaGenerator:
    def __init__(self, docs_dir: Path, base_url: str = "https://docs.pheno-sdk.com"):
        self.docs_dir = docs_dir
        self.base_url = base_url
        self.generated_count = 0
        
    def get_canonical_url(self, rel_path: Path) -> str:
        """Generate canonical URL for a page."""
        # Remove .mdx extension and convert to URL path
        path_str = str(rel_path).replace('.mdx', '').replace('index', '')
        path_str = path_str.replace('\\', '/')
        
        # Remove trailing slash for consistency
        if path_str.endswith('/'):
            path_str = path_str[:-1]
        
        return f"{self.base_url}/docs/{path_str}"
    
    def generate_og_image_url(self, rel_path: Path) -> str:
        """Generate OG image URL based on section."""
        parts = rel_path.parts
        section = parts[0] if parts else "docs"
        
        return f"{self.base_url}/images/og/{section.lower()}-default.png"
    
    def inject_seo_meta(self, filepath: Path) -> bool:
        """Inject SEO meta tags into a file's frontmatter."""
        try:
            content = filepath.read_text(encoding='utf-8')
            rel_path = filepath.relative_to(self.docs_dir)
            
            # Extract existing frontmatter
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return False
            
            frontmatter = match.group(1)
            rest_of_content = content[len(match.group(0))+1:]
            
            # Generate SEO values
            canonical_url = self.get_canonical_url(rel_path)
            og_image = self.generate_og_image_url(rel_path)
            
            # Check if SEO meta already exists
            if 'canonicalUrl:' in frontmatter:
                return True  # Already has SEO meta
            
            # Add SEO meta to frontmatter
            new_lines = [
                '',
                f'# SEO & Social',
                f'canonicalUrl: "{canonical_url}"',
                f'ogImage: "{og_image}"',
                f'ogType: "article"',
            ]
            
            frontmatter_with_seo = frontmatter + '\n'.join(new_lines)
            
            # Reconstruct file
            new_content = f"---\n{frontmatter_with_seo}\n---{rest_of_content}"
            filepath.write_text(new_content, encoding='utf-8')
            
            return True
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return False
    
    def generate_structured_data(self, filepath: Path, title: str, description: str) -> Dict:
        """Generate schema.org structured data for a page."""
        rel_path = filepath.relative_to(self.docs_dir)
        canonical_url = self.get_canonical_url(rel_path)
        
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "url": canonical_url,
            "author": {
                "@type": "Organization",
                "name": "PhenoSDK"
            },
            "publisher": {
                "@type": "Organization",
                "name": "PhenoSDK",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.base_url}/logo.png"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat()
        }
    
    def run(self):
        """Process all MDX files."""
        mdx_files = list(self.docs_dir.rglob("*.mdx"))
        mdx_files = [f for f in mdx_files if f.name != "index.mdx"]
        
        print(f"\n🌐 Generating SEO meta for {len(mdx_files)} files...")
        print("="*80)
        
        success = 0
        skipped = 0
        
        for i, mdx_file in enumerate(mdx_files, 1):
            if self.inject_seo_meta(mdx_file):
                success += 1
                if i % 100 == 0:
                    print(f"✅ {i:3d}/{len(mdx_files)} - SEO meta added")
            else:
                skipped += 1
        
        print("="*80)
        print(f"\n📊 SEO Meta Generation Complete")
        print(f"   Total files: {len(mdx_files)}")
        print(f"   Successfully processed: {success}")
        print(f"   Skipped (already has SEO): {skipped}")

def generate_sitemap(docs_dir: Path, output_file: Path, base_url: str = "https://docs.pheno-sdk.com"):
    """Generate sitemap.xml for search engine crawling."""
    mdx_files = list(docs_dir.rglob("*.mdx"))
    
    urls = []
    for mdx_file in sorted(mdx_files):
        if mdx_file.name == "index.mdx":
            continue
        
        rel_path = str(mdx_file.relative_to(docs_dir)).replace('.mdx', '').replace('\\', '/')
        
        # Get modification time
        mtime = mdx_file.stat().st_mtime
        from datetime import datetime as dt
        lastmod = dt.fromtimestamp(mtime).isoformat()
        
        url = f"{base_url}/docs/{rel_path}"
        
        urls.append({
            'loc': url,
            'lastmod': lastmod,
            'changefreq': 'weekly',
            'priority': '0.8'
        })
    
    # Generate XML
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url_info in urls:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{url_info["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{url_info["lastmod"]}</lastmod>')
        xml_lines.append(f'    <changefreq>{url_info["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{url_info["priority"]}</priority>')
        xml_lines.append('  </url>')
    
    xml_lines.append('</urlset>')
    
    output_file.write_text('\n'.join(xml_lines))
    return len(urls)

def generate_robots_txt(output_file: Path, base_url: str = "https://docs.pheno-sdk.com"):
    """Generate robots.txt for search engine guidance."""
    robots_content = f"""# Robots.txt for {base_url}
User-agent: *
Allow: /
Allow: /docs/
Allow: /images/

Disallow: /.git/
Disallow: /.next/
Disallow: /node_modules/
Disallow: /__pycache__/

# Sitemap
Sitemap: {base_url}/sitemap.xml

# Crawl delay (in seconds)
Crawl-delay: 1
"""
    
    output_file.write_text(robots_content)

def main():
    docs_dir = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/apps/docs/content/docs")
    static_dir = Path("/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/apps/docs/public")
    
    # Generate SEO meta in all files
    generator = SEOMetaGenerator(docs_dir)
    generator.run()
    
    # Generate sitemap
    print("\n🗺️  Generating sitemap.xml...")
    sitemap_path = static_dir / "sitemap.xml"
    sitemap_path.parent.mkdir(parents=True, exist_ok=True)
    urls_count = generate_sitemap(docs_dir, sitemap_path)
    print(f"✅ Sitemap generated: {urls_count} URLs")
    
    # Generate robots.txt
    print("\n🤖 Generating robots.txt...")
    robots_path = static_dir / "robots.txt"
    generate_robots_txt(robots_path)
    print(f"✅ robots.txt generated")
    
    print("\n" + "="*80)
    print("📊 PHASE 4B: SEO OPTIMIZATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
