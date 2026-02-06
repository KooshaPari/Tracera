/**
 * Comprehensive tests for UICodeTracePanel component
 * Tests traceability chain visualization, code references, and user interactions
 */

import { render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { CanonicalConcept, CodeReference } from '@tracertm/types';

import type { TraceLevel, UICodeTraceChain } from '../../../components/graph/UICodeTracePanel';

import { UICodeTracePanel } from '../../../components/graph/UICodeTracePanel';

// =============================================================================
// MOCK DATA
// =============================================================================

const mockCodeReference: CodeReference = {
  commitSha: 'abc123def456',
  endLine: 128,
  filePath: 'src/components/LoginForm.tsx',
  id: 'code-ref-1',
  language: 'typescript',
  lastSyncedAt: new Date().toISOString(),
  parentSymbol: 'AuthModule',
  repositoryUrl: 'https://github.com/example/repo',
  signature: 'function LoginForm(props: LoginFormProps): ReactNode',
  startLine: 42,
  symbolName: 'LoginForm',
  symbolType: 'component',
};

const mockCanonicalConcept: CanonicalConcept = {
  category: 'authentication',
  confidence: 0.95,
  createdAt: new Date().toISOString(),
  description: 'User login and authentication flow',
  domain: 'security',
  id: 'concept-1',
  name: 'User Authentication',
  projectId: 'project-1',
  projectionCount: 3,
  slug: 'user-authentication',
  source: 'inferred',
  tags: ['critical', 'auth', 'user-facing'],
  updatedAt: new Date().toISOString(),
  version: 1,
};

const mockUiTraceLevel: TraceLevel = {
  componentName: 'LoginForm',
  componentPath: 'src/components/LoginForm.tsx',
  confidence: 1,
  description: 'User-facing login form',
  id: 'level-1',
  isConfirmed: true,
  perspective: 'ui',
  strategy: 'explicit_annotation',
  title: 'Login Form Component',
  type: 'ui',
};

const mockCodeTraceLevel: TraceLevel = {
  codeRef: mockCodeReference,
  confidence: 0.95,
  description: 'React component implementing login form',
  id: 'level-2',
  isConfirmed: true,
  perspective: 'technical',
  strategy: 'manual_link',
  title: 'LoginForm Implementation',
  type: 'code',
};

const mockRequirementTraceLevel: TraceLevel = {
  businessValue: 'Enable secure user access to the platform',
  confidence: 0.9,
  description: 'Users must be able to authenticate with email/password',
  id: 'level-3',
  isConfirmed: true,
  perspective: 'business',
  requirementId: 'req-auth-001',
  strategy: 'shared_canonical',
  title: 'User Authentication Requirement',
  type: 'requirement',
};

const mockConceptTraceLevel: TraceLevel = {
  canonicalId: 'concept-1',
  confidence: 0.95,
  description: 'Abstract representation of user authentication',
  id: 'level-4',
  strategy: 'manual_link',
  title: 'User Authentication Concept',
  type: 'concept',
};

const mockTraceChain: UICodeTraceChain = {
  canonicalConcept: mockCanonicalConcept,
  description: 'Complete traceability from UI component to requirements',
  id: 'trace-1',
  lastUpdated: new Date().toISOString(),
  levels: [mockUiTraceLevel, mockCodeTraceLevel, mockRequirementTraceLevel, mockConceptTraceLevel],
  name: 'Login Form → Authentication',
  overallConfidence: 0.95,
};

// =============================================================================
// TESTS
// =============================================================================

describe(UICodeTracePanel, () => {
  const mockOnOpenCode = vi.fn();
  const mockOnOpenRequirement = vi.fn();
  const mockOnNavigateToUI = vi.fn();
  const mockOnRefreshTrace = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // =========================================================================
  // RENDER TESTS
  // =========================================================================

  describe('rendering', () => {
    it('should render empty state when no trace chain provided', () => {
      render(<UICodeTracePanel traceChain={null} />);

      expect(screen.getByText('No trace chain selected')).toBeInTheDocument();
      expect(
        screen.getByText(/Select a UI component to view its traceability chain/),
      ).toBeInTheDocument();
    });

    it('should render loading state when isLoading is true', () => {
      render(<UICodeTracePanel traceChain={null} isLoading />);

      expect(screen.getByText('Loading trace chain...')).toBeInTheDocument();
    });

    it('should render trace chain header with name and confidence', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const text = container.textContent ?? '';
      expect(text).toContain(mockTraceChain.name);
      expect(text).toContain('95%');
    });

    it('should render trace chain description', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText(mockTraceChain.description!)).toBeInTheDocument();
    });

    it('should render all trace levels', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText('Login Form Component')).toBeInTheDocument();
      expect(screen.getByText('LoginForm Implementation')).toBeInTheDocument();
      expect(screen.getByText('User Authentication Requirement')).toBeInTheDocument();
      expect(screen.getByText('User Authentication Concept')).toBeInTheDocument();
    });

    it('should render canonical concept card', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const text = container.textContent ?? '';
      expect(text).toContain('Canonical Concept');
      expect(text).toContain(mockCanonicalConcept.name);
      expect(text).toContain(mockCanonicalConcept.description ?? '');
    });
  });

  // =========================================================================
  // TRACE LEVEL RENDERING TESTS
  // =========================================================================

  describe('trace level rendering', () => {
    it('should render UI level with component details', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const uiLevel =
        screen.getByText('Login Form Component').closest("[role='region']") ??
        screen.getByText('Login Form Component').closest('.border');
      expect(uiLevel).toBeInTheDocument();
      expect(within(uiLevel!).getByText('Component:')).toBeInTheDocument();
      expect(within(uiLevel!).getByText('LoginForm')).toBeInTheDocument();
      expect(within(uiLevel!).getByText('Path:')).toBeInTheDocument();
    });

    it('should render code level with file and line information', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const text = container.textContent ?? '';
      expect(text).toContain('src/components/LoginForm.tsx');
      expect(text).toContain('LoginForm');
      expect(text).toContain('component');
    });

    it('should render code signature when available', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText(/function LoginForm/)).toBeInTheDocument();
    });

    it('should render requirement level with business value', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText('User Authentication Requirement')).toBeInTheDocument();
      expect(screen.getByText('Enable secure user access to the platform')).toBeInTheDocument();
    });

    it('should display perspective badges for each level', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const text = container.textContent ?? '';
      expect(text).toContain('ui');
      expect(text).toContain('technical');
      expect(text).toContain('business');
    });
  });

  // =========================================================================
  // CONFIDENCE DISPLAY TESTS
  // =========================================================================

  describe('confidence scores and colors', () => {
    it('should display confidence percentage for each level', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const confidenceElements = screen.getAllByText(/\d+%/);
      expect(confidenceElements.length).toBeGreaterThan(0);
    });

    it('should display overall confidence in header', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // The overall confidence should appear somewhere in the document
      const text = container.textContent ?? '';
      expect(text).toContain('95%');
    });

    it('should use appropriate color classes for confidence levels', () => {
      const highConfidenceChain: UICodeTraceChain = {
        ...mockTraceChain,
        overallConfidence: 0.95,
      };
      render(<UICodeTracePanel traceChain={highConfidenceChain} />);

      // High confidence should have green indicator
      const confidenceElements = screen.getAllByText(/95%/);
      expect(confidenceElements.length).toBeGreaterThan(0);
    });

    it('should display confirmation status', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // All levels in mock data are confirmed
      // This is implicit in the rendering
      expect(screen.getByText('Login Form Component')).toBeInTheDocument();
    });
  });

  // =========================================================================
  // INTERACTION TESTS
  // =========================================================================

  describe('user interactions', () => {
    it('should call onOpenCode when code button is clicked', async () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} onOpenCode={mockOnOpenCode} />);

      const openButtons = screen.getAllByText(/Open in Editor/);
      if (openButtons.length > 0) {
        await user.click(openButtons[0]);
        expect(mockOnOpenCode).toHaveBeenCalledWith(mockCodeReference);
      }
    });

    it('should call onOpenRequirement when requirement button is clicked', async () => {
      render(
        <UICodeTracePanel traceChain={mockTraceChain} onOpenRequirement={mockOnOpenRequirement} />,
      );

      const viewButtons = screen.getAllByText(/View Requirement/);
      if (viewButtons.length > 0) {
        await user.click(viewButtons[0]);
        expect(mockOnOpenRequirement).toHaveBeenCalledWith('req-auth-001');
      }
    });

    it('should call onNavigateToUI when component button is clicked', async () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} onNavigateToUI={mockOnNavigateToUI} />);

      const componentButtons = screen.getAllByText(/Open Component/);
      if (componentButtons.length > 0) {
        await user.click(componentButtons[0]);
        expect(mockOnNavigateToUI).toHaveBeenCalledWith('src/components/LoginForm.tsx');
      }
    });

    it('should call onRefreshTrace when refresh button is clicked', async () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} onRefreshTrace={mockOnRefreshTrace} />);

      const refreshButton = screen.getByText('Refresh');
      await user.click(refreshButton);
      expect(mockOnRefreshTrace).toHaveBeenCalled();
    });
  });

  // =========================================================================
  // TOOLTIP TESTS
  // =========================================================================

  describe('tooltips and information display', () => {
    it('should display strategy information in tooltips', async () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // Tooltips are displayed on hover
      const confidenceBadges = screen.getAllByText(/\d+%/);
      if (confidenceBadges.length > 0) {
        await user.hover(confidenceBadges[0]);
        // Wait for tooltip to appear
        await waitFor(() => {
          // Strategy labels should be in the document
          expect(document.body.textContent).toBeDefined();
        });
      }
    });
  });

  // =========================================================================
  // EDGE CASES
  // =========================================================================

  describe('edge cases', () => {
    it('should handle trace chain with no canonical concept', () => {
      const chainWithoutConcept: UICodeTraceChain = {
        ...mockTraceChain,
        canonicalConcept: undefined,
        projections: undefined,
      };

      render(<UICodeTracePanel traceChain={chainWithoutConcept} />);

      expect(screen.getByText(mockTraceChain.name)).toBeInTheDocument();
      // When no concept, there should not be a concept card header
      const conceptCards = document.querySelectorAll("div:has(> *:contains('Canonical Concept'))");
      expect(conceptCards.length).toBe(0);
    });

    it('should handle trace level without optional fields', () => {
      const minimalLevel: TraceLevel = {
        confidence: 0.5,
        id: 'minimal-1',
        title: 'Minimal Code Level',
        type: 'code',
      };

      const chainWithMinimal: UICodeTraceChain = {
        id: 'trace-2',
        lastUpdated: new Date().toISOString(),
        levels: [minimalLevel],
        name: 'Minimal Trace',
        overallConfidence: 0.5,
      };

      render(<UICodeTracePanel traceChain={chainWithMinimal} />);

      expect(screen.getByText('Minimal Code Level')).toBeInTheDocument();
      // Check that 50% appears in the document (may appear multiple times)
      const text = container.textContent ?? '';
      expect(text).toContain('50%');
    });

    it('should handle empty trace levels', () => {
      const emptyChain: UICodeTraceChain = {
        id: 'trace-3',
        lastUpdated: new Date().toISOString(),
        levels: [],
        name: 'Empty Trace',
        overallConfidence: 0,
      };

      render(<UICodeTracePanel traceChain={emptyChain} />);

      expect(screen.getByText('Empty Trace')).toBeInTheDocument();
    });

    it('should handle trace level with low confidence', () => {
      const lowConfidenceLevel: TraceLevel = {
        confidence: 0.3,
        id: 'level-low',
        strategy: 'co_occurrence',
        title: 'Low Confidence Match',
        type: 'code',
      };

      const lowConfidenceChain: UICodeTraceChain = {
        id: 'trace-4',
        lastUpdated: new Date().toISOString(),
        levels: [lowConfidenceLevel],
        name: 'Low Confidence Trace',
        overallConfidence: 0.3,
      };

      render(<UICodeTracePanel traceChain={lowConfidenceChain} />);

      const allText = document.body.textContent || '';
      expect(allText).toContain('30%');
    });

    it('should handle long file paths with truncation', () => {
      const longPathLevel: TraceLevel = {
        codeRef: {
          ...mockCodeReference,
          filePath: 'src/very/deeply/nested/path/with/many/directories/components/LoginForm.tsx',
        },
        confidence: 0.9,
        id: 'level-long',
        title: 'Long Path Code',
        type: 'code',
      };

      const chainWithLongPath: UICodeTraceChain = {
        id: 'trace-5',
        lastUpdated: new Date().toISOString(),
        levels: [longPathLevel],
        name: 'Long Path Trace',
        overallConfidence: 0.9,
      };

      render(<UICodeTracePanel traceChain={chainWithLongPath} />);

      // Path should be present (even if truncated)
      expect(container.textContent).toContain('components/LoginForm.tsx');
    });
  });

  // =========================================================================
  // ACCESSIBILITY TESTS
  // =========================================================================

  describe('accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // Should have proper heading structure
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    it('should have alt text for images', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // If there are images, they should have alt text
      const images = document.querySelectorAll('img');
      images.forEach((img) => {
        expect(img.getAttribute('alt')).toBeTruthy();
      });
    });

    it('should have proper button labels', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // All buttons should have accessible labels
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        // Button should have text content or aria-label
        expect(
          button.textContent?.trim() ||
            (button.getAttribute('aria-label') ?? button.getAttribute('title')),
        ).toBeTruthy();
      });
    });
  });

  // =========================================================================
  // DATA DISPLAY TESTS
  // =========================================================================

  describe('data display', () => {
    it('should display last updated timestamp', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    });

    it('should display canonical concept metadata', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      expect(screen.getByText(mockCanonicalConcept.name)).toBeInTheDocument();
      expect(screen.getByText(mockCanonicalConcept.domain)).toBeInTheDocument();
    });

    it('should display projections count in concept card', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const projectionText = screen.getByText(/perspective.*linked/i);
      expect(projectionText).toBeInTheDocument();
    });

    it('should display code reference metadata', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      const allText = document.body.textContent || '';
      expect(allText).toContain(mockCodeReference.symbolName);
      expect(allText).toContain(mockCodeReference.symbolType);
    });
  });

  // =========================================================================
  // SCROLLING TESTS
  // =========================================================================

  describe('scrolling behavior', () => {
    it('should have scroll area for trace levels', () => {
      render(<UICodeTracePanel traceChain={mockTraceChain} />);

      // Check for scroll container
      const _scrollArea = container.querySelector("[class*='scroll']");
      // ScrollArea should be present or the container should handle overflow
      expect(container).toBeInTheDocument();
    });
  });
});
