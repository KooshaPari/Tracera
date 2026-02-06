# Figma Design Generator - Documentation Index

Quick navigation for all Figma generator documentation and files.

## Getting Started

1. **[QUICK_START.md](./QUICK_START.md)** - Start here!
   - 5-minute setup guide
   - Step-by-step instructions
   - First sync walkthrough

2. **[README.md](./README.md)** - Complete reference
   - Full feature documentation
   - API reference
   - Configuration guide
   - Troubleshooting

3. **[EXAMPLES.md](./EXAMPLES.md)** - Learn by example
   - Button component example
   - Card component example
   - Token extraction workflows
   - CI/CD integration examples

4. **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Deep dive
   - Architecture overview
   - Feature breakdown
   - Integration points
   - Success metrics

## Core Files

### Implementation Files

- **[figma-api-client.ts](./figma-api-client.ts)**
  - Figma REST API wrapper
  - Rate limiting
  - File/component/token operations

- **[code-to-design.ts](./code-to-design.ts)**
  - React component parser
  - Tailwind → Figma converter
  - JSX → Figma node tree

- **[generate-figma.ts](./generate-figma.ts)**
  - Main generator
  - Plugin format output
  - story.to.design output

- **[sync-designs.ts](./sync-designs.ts)**
  - Bidirectional sync
  - Conflict detection
  - Metadata management

### Configuration Files

- **[config.ts](./config.ts)**
  - Environment configuration
  - Design token defaults
  - Path configuration

- **[types.ts](./types.ts)**
  - TypeScript type definitions
  - Figma API types
  - Component types

- **[index.ts](./index.ts)**
  - Public API exports
  - Entry point

### Package Files

- **[package.json](./package.json)**
  - Dependencies
  - Scripts

- **[.env.figma.example](../.env.figma.example)**
  - Environment variable template

## Quick Commands Reference

```bash
# Setup
cp .env.figma.example .env.local
bun install

# Sync
bun run figma:sync              # Two-way sync
bun run figma:push              # Push only
bun run figma:pull              # Pull only

# Export
bun run figma:export            # Generate plugin
bun run figma:export-tokens     # Export tokens

# Utilities
bun run figma:conflicts         # Check conflicts
bun run figma:upload            # story.to.design
```

## Feature Documentation

### Figma API Client

**File:** [figma-api-client.ts](./figma-api-client.ts)

**Key Features:**

- File data retrieval
- Component extraction
- Image export
- Design token extraction
- Version history
- Comment retrieval
- Rate limiting

**Documentation:**

- [README.md - Figma API Client](./README.md#figma-plugin-usage)
- [EXAMPLES.md - API Usage](./EXAMPLES.md#example-3-design-token-extraction)

### Code to Design Converter

**File:** [code-to-design.ts](./code-to-design.ts)

**Key Features:**

- TypeScript AST parsing
- Component structure extraction
- Tailwind class parsing
- Figma property mapping

**Documentation:**

- [README.md - Tailwind Mapping](./README.md#tailwind--figma-mapping)
- [EXAMPLES.md - Component Examples](./EXAMPLES.md#example-1-button-component)

### Generator

**File:** [generate-figma.ts](./generate-figma.ts)

**Key Features:**

- Figma plugin generation
- story.to.design output
- Storybook story generation

**Documentation:**

- [README.md - Generate Plugin](./README.md#generate-figma-plugin)
- [EXAMPLES.md - Plugin Export](./EXAMPLES.md#example-6-component-library)

### Sync Manager

**File:** [sync-designs.ts](./sync-designs.ts)

**Key Features:**

- Bidirectional sync
- Conflict detection
- Metadata management
- Token export

**Documentation:**

- [README.md - Sync Designs](./README.md#sync-with-figma)
- [EXAMPLES.md - Sync Workflow](./EXAMPLES.md#example-4-sync-workflow)

## Workflows

### Initial Setup

1. [QUICK_START.md - Setup](./QUICK_START.md#step-2-configure-environment)
2. [README.md - Configuration](./README.md#configuration)

### Component Export

1. [EXAMPLES.md - Button Export](./EXAMPLES.md#example-1-button-component)
2. [README.md - Plugin Usage](./README.md#figma-plugin-usage)

### Design Token Sync

1. [EXAMPLES.md - Token Export](./EXAMPLES.md#example-3-design-token-extraction)
2. [README.md - Export Tokens](./README.md#export-design-tokens)

### CI/CD Integration

1. [EXAMPLES.md - GitHub Actions](./EXAMPLES.md#example-5-cicd-integration)
2. [QUICK_START.md - Workflow Integration](./QUICK_START.md#workflow-integration)

## API Reference

### Classes

- **FigmaClient** - [figma-api-client.ts](./figma-api-client.ts)
- **TailwindConverter** - [code-to-design.ts](./code-to-design.ts)
- **ComponentParser** - [code-to-design.ts](./code-to-design.ts)
- **FigmaGenerator** - [generate-figma.ts](./generate-figma.ts)
- **DesignSync** - [sync-designs.ts](./sync-designs.ts)

### Types

See [types.ts](./types.ts) for complete type definitions:

- Figma API types
- Component definition types
- Design token types
- Sync metadata types
- Configuration types
- Error types

### Configuration

See [config.ts](./config.ts) for:

- Environment variables
- Default design tokens
- Component paths
- Output configuration

## Troubleshooting

### Common Issues

1. **Authentication**
   - [README.md - Troubleshooting](./README.md#troubleshooting)
   - [QUICK_START.md - Credentials](./QUICK_START.md#step-1-get-figma-credentials)

2. **Conflicts**
   - [README.md - Check Conflicts](./README.md#check-for-conflicts)
   - [EXAMPLES.md - Conflict Resolution](./EXAMPLES.md#example-4-sync-workflow)

3. **Rate Limiting**
   - [README.md - Rate Limit](./README.md#rate-limit-exceeded)
   - [config.ts - Rate Config](./config.ts)

## Environment Variables

See [.env.figma.example](../.env.figma.example)

**Required:**

- `FIGMA_ACCESS_TOKEN`
- `FIGMA_FILE_KEY`

**Optional:**

- `STORY_TO_DESIGN_URL`
- `FIGMA_OUTPUT_DIR`
- `FIGMA_OUTPUT_FORMAT`
- `FIGMA_CONFLICT_RESOLUTION`
- `FIGMA_RATE_LIMIT_REQUESTS`
- `FIGMA_RATE_LIMIT_MS`

## File Structure

```
tools/figma-generator/
├── Core Implementation
│   ├── figma-api-client.ts      # Figma API wrapper
│   ├── code-to-design.ts        # React → Figma
│   ├── generate-figma.ts        # Generator
│   └── sync-designs.ts          # Sync manager
│
├── Configuration
│   ├── config.ts                # Config + tokens
│   ├── types.ts                 # Type definitions
│   └── index.ts                 # Public API
│
├── Documentation
│   ├── INDEX.md                 # This file
│   ├── README.md                # Complete reference
│   ├── QUICK_START.md          # Setup guide
│   ├── IMPLEMENTATION_SUMMARY.md # Architecture
│   └── EXAMPLES.md             # Examples
│
└── Package
    ├── package.json             # Dependencies
    └── .env.figma.example       # Env template
```

## External Resources

### Figma Resources

- [Figma API Documentation](https://www.figma.com/developers/api)
- [Get Access Token](https://www.figma.com/developers/api#authentication)
- [Figma Plugin API](https://www.figma.com/plugin-docs/)

### story.to.design

- [story.to.design Website](https://story.to.design)
- [Storybook Addon Designs](https://storybook.js.org/addons/@storybook/addon-designs)

### Related Tools

- [figma-api npm package](https://www.npmjs.com/package/figma-api)
- [TypeScript AST Viewer](https://ts-ast-viewer.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Version History

### v1.0.0 - November 30, 2025

- Initial release
- Complete Figma API integration
- Bidirectional sync
- Plugin generation
- story.to.design support
- Design token extraction
- Comprehensive documentation

## Support

For issues or questions:

1. Check this index for relevant documentation
2. Review [README.md](./README.md) troubleshooting section
3. Examine [EXAMPLES.md](./EXAMPLES.md) for usage patterns
4. Review [types.ts](./types.ts) for API types

## License

Part of the TracerTM project. See main LICENSE file.

---

**Last Updated:** November 30, 2025
**Version:** 1.0.0
**Status:** Production Ready ✅
