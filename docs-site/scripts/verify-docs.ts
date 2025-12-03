#!/usr/bin/env bun
/**
 * Documentation Verification Script
 *
 * Verifies that all generated MDX files are valid and properly formatted.
 *
 * Usage: bun run scripts/verify-docs.ts
 */

import { readdir, readFile, stat } from 'fs/promises'
import { join } from 'path'

const DOCS_BASE_DIR = join(process.cwd(), 'content', 'docs')

interface VerificationResult {
  totalFiles: number
  validFiles: number
  invalidFiles: number
  emptyFiles: number
  missingFrontmatter: number
  errors: Array<{ file: string; error: string }>
}

/**
 * Recursively find all index.mdx files
 */
async function findMDXFiles(dir: string): Promise<string[]> {
  const files: string[] = []
  const entries = await readdir(dir, { withFileTypes: true })

  for (const entry of entries) {
    const fullPath = join(dir, entry.name)

    if (entry.isDirectory()) {
      const subFiles = await findMDXFiles(fullPath)
      files.push(...subFiles)
    } else if (entry.name === 'index.mdx') {
      files.push(fullPath)
    }
  }

  return files
}

/**
 * Verify a single MDX file
 */
async function verifyMDXFile(filePath: string): Promise<{ valid: boolean; error?: string }> {
  try {
    const content = await readFile(filePath, 'utf-8')

    // Check if file is empty
    if (content.trim().length === 0) {
      return { valid: false, error: 'Empty file' }
    }

    // Check for frontmatter
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/)
    if (!frontmatterMatch) {
      return { valid: false, error: 'Missing frontmatter' }
    }

    const frontmatter = frontmatterMatch[1]

    // Check for required fields
    if (!frontmatter.includes('title:')) {
      return { valid: false, error: 'Missing title in frontmatter' }
    }

    if (!frontmatter.includes('description:')) {
      return { valid: false, error: 'Missing description in frontmatter' }
    }

    // Check for content after frontmatter
    const body = content.substring(frontmatterMatch[0].length).trim()
    if (body.length < 50) {
      return { valid: false, error: 'Content too short (less than 50 characters)' }
    }

    // Check for h1 heading
    if (!body.match(/^#\s+.+/m)) {
      return { valid: false, error: 'Missing h1 heading' }
    }

    return { valid: true }
  } catch (error) {
    return { valid: false, error: `Read error: ${error}` }
  }
}

/**
 * Main verification function
 */
async function main() {
  console.log('🔍 TraceRTM Documentation Verification\n')
  console.log('Base directory:', DOCS_BASE_DIR)
  console.log('Finding MDX files...\n')

  const result: VerificationResult = {
    totalFiles: 0,
    validFiles: 0,
    invalidFiles: 0,
    emptyFiles: 0,
    missingFrontmatter: 0,
    errors: []
  }

  try {
    const files = await findMDXFiles(DOCS_BASE_DIR)
    result.totalFiles = files.length

    console.log(`Found ${files.length} MDX files`)
    console.log('Verifying...\n')

    let processed = 0
    for (const file of files) {
      processed++
      const progress = Math.round((processed / files.length) * 100)
      process.stdout.write(`\r[${progress}%] Verifying ${processed}/${files.length}`)

      const verification = await verifyMDXFile(file)

      if (verification.valid) {
        result.validFiles++
      } else {
        result.invalidFiles++

        if (verification.error?.includes('Empty file')) {
          result.emptyFiles++
        } else if (verification.error?.includes('frontmatter')) {
          result.missingFrontmatter++
        }

        result.errors.push({
          file: file.replace(DOCS_BASE_DIR, ''),
          error: verification.error || 'Unknown error'
        })
      }
    }

    console.log('\n\n✨ Verification complete!\n')

    // Display summary
    console.log('📊 Summary:')
    console.log(`   Total files: ${result.totalFiles}`)
    console.log(`   Valid files: ${result.validFiles} (${Math.round((result.validFiles / result.totalFiles) * 100)}%)`)
    console.log(`   Invalid files: ${result.invalidFiles}`)

    if (result.emptyFiles > 0) {
      console.log(`   Empty files: ${result.emptyFiles}`)
    }

    if (result.missingFrontmatter > 0) {
      console.log(`   Missing frontmatter: ${result.missingFrontmatter}`)
    }

    // Display errors if any
    if (result.errors.length > 0) {
      console.log('\n❌ Errors found:')
      result.errors.forEach(({ file, error }) => {
        console.log(`   ${file}: ${error}`)
      })
    } else {
      console.log('\n✅ All files are valid!')
    }

    // Sample random files
    console.log('\n📄 Sample files:')
    const samples = files.sort(() => Math.random() - 0.5).slice(0, 5)
    for (const sample of samples) {
      const content = await readFile(sample, 'utf-8')
      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/)
      if (frontmatterMatch) {
        const titleMatch = frontmatterMatch[1].match(/title:\s*['"]?([^'"]+)['"]?/)
        const title = titleMatch ? titleMatch[1] : 'Unknown'
        console.log(`   ${sample.replace(DOCS_BASE_DIR, '')}`)
        console.log(`      Title: ${title}`)
      }
    }

  } catch (error) {
    console.error('\n❌ Error during verification:', error)
    process.exit(1)
  }
}

// Run the script
main()
