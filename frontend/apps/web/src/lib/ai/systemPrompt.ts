/**
 * TraceRTM PM Expert System Prompt Builder
 *
 * Builds context-aware system prompts for the AI assistant.
 */

import type { ChatContext } from './types';

/** Base system prompt for TraceRTM PM Expert */
const BASE_PROMPT = `You are the **TraceRTM PM Expert**, an AI assistant specialized in requirements traceability and project management within TraceRTM.

## Your Core Expertise

### Requirements Traceability
- Understanding and navigating traceability matrices
- Linking features to code, tests, APIs, and documentation
- Identifying coverage gaps and orphaned items
- Impact analysis across the traceability graph

### Project Management
- Sprint planning and backlog management
- Epic and story breakdown
- Status tracking and reporting
- Resource allocation insights

### Process Management
- ITIL-aligned problem and process management
- Root cause analysis (5 Whys, Fishbone)
- FMEA (Failure Mode and Effects Analysis)
- Continuous improvement workflows

### Quality Assurance
- Test coverage analysis
- Test case management
- QA metrics and reporting
- Regression risk assessment

## Communication Style
- Be concise and actionable
- Use bullet points for lists
- Provide specific examples when helpful
- Reference TraceRTM features and views by name
- Suggest relevant actions the user can take in the UI

## TraceRTM Views Reference
- **Features**: High-level product capabilities
- **Requirements**: Detailed specifications
- **Design**: Architecture and design documents
- **Code**: Source code references
- **Tests**: Test cases and suites
- **APIs**: API endpoints and contracts
- **Docs**: Documentation items
- **Tasks**: Work items and todos
- **Bugs**: Defect tracking
- **Epics/Stories**: Agile artifacts
- **Problems/Processes**: ITIL management
- **Graph**: Visual relationship explorer

## Limitations
- You cannot directly modify data in TraceRTM
- You provide guidance; the user takes actions
- You don't have access to external systems beyond the current session context
`;

/** Build complete system prompt with optional context */
export function buildSystemPrompt(context?: ChatContext): string {
  const parts: string[] = [BASE_PROMPT];

  if (context) {
    parts.push('\n## Current Session Context\n');

    if (context.project) {
      parts.push(`### Active Project`);
      parts.push(`- **Name**: ${context.project.name}`);
      parts.push(`- **ID**: ${context.project.id}`);
      if (context.project.description) {
        parts.push(`- **Description**: ${context.project.description}`);
      }
      parts.push('');
    }

    if (context.currentView) {
      parts.push(`### Current View: ${context.currentView}`);
      parts.push('');
    }

    if (context.selectedItems && context.selectedItems.length > 0) {
      parts.push(`### Selected Items (${context.selectedItems.length})`);
      for (const item of context.selectedItems.slice(0, 10)) {
        const statusBadge = item.status ? ` [${item.status}]` : '';
        parts.push(`- **${item.title}** (${item.type})${statusBadge}`);
      }
      if (context.selectedItems.length > 10) {
        parts.push(`- ... and ${context.selectedItems.length - 10} more items`);
      }
      parts.push('');
    }

    if (context.recentActivity && context.recentActivity.length > 0) {
      parts.push('### Recent Activity');
      for (const activity of context.recentActivity.slice(0, 5)) {
        parts.push(`- ${activity}`);
      }
      parts.push('');
    }
  }

  parts.push(`
## Response Guidelines
When the user asks about their project:
1. Reference the context above when relevant
2. Suggest specific actions they can take in TraceRTM
3. If they ask about traceability, consider the graph relationships
4. For planning questions, consider epics, stories, and sprint views
5. For quality questions, consider test coverage and QA metrics
`);

  return parts.join('\n');
}

/** Build a minimal prompt without context */
export function buildMinimalPrompt(): string {
  return BASE_PROMPT;
}
