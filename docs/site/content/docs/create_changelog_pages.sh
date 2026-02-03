#\!/bin/bash

create_page() {
  local dir=$1
  local title=$2
  
  if [ \! -f "$dir/index.mdx" ]; then
    mkdir -p "$dir"
    cat > "$dir/index.mdx" << CONTENT
---
title: $title
description: Release notes for $title
---

# $title

Release notes and changelog for **$title**.

## Overview

This page contains the release notes and changelog for $title.

## What's New

- New features and improvements
- Bug fixes and patches
- Performance enhancements
- Security updates
- Breaking changes

## Migration Guide

If you're upgrading from a previous version, check the migration guide for important changes.

## Download

Download the latest version from our [releases page](https://github.com/yourusername/tracertm/releases).

## Support

- Report issues on [GitHub](https://github.com/yourusername/tracertm/issues)
- Join our [community discussions](https://github.com/yourusername/tracertm/discussions)
- Contact support

---

**Last Updated**: $(date +%Y-%m-%d)
CONTENT
    echo "✅ Created: $dir/index.mdx"
  fi
}

# Changelog
create_page "04-changelog" "Changelog"
create_page "04-changelog/01-v2.0" "v2.0"
create_page "04-changelog/02-v1.5" "v1.5"
create_page "04-changelog/03-v1.0" "v1.0"

echo ""
echo "✅ Changelog pages created\!"
