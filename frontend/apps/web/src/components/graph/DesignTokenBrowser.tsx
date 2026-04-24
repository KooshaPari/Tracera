// DesignTokenBrowser.tsx - Browse, search, and manage design tokens
// Displays design tokens organized by category with previews and component usage

import type { CSSProperties } from 'react';

import {
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Code,
  Copy,
  ExternalLink,
  Eye,
  Figma,
  FileCode,
  Hash,
  Layers,
  Link as LinkIcon,
  Maximize,
  Palette,
  Play,
  Search,
  Zap,
} from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type { DesignToken, DesignTokenType } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui/components/Card';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@tracertm/ui/components/Collapsible';
import { Input } from '@tracertm/ui/components/Input';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// =============================================================================
// TYPES
// =============================================================================

export interface DesignTokenBrowserProps {
  /** Design tokens to display */
  tokens: DesignToken[];
  /** Callback when a token is selected */
  onSelectToken?: (tokenId: string) => void;
  /** Currently selected token ID */
  selectedTokenId?: string | null;
  /** Callback to link token to Figma style */
  onLinkToFigma?: (tokenId: string) => void;
  /** Show component usage details */
  showComponentUsage?: boolean;
  /** All components (for usage lookup) */
  componentMap?: Map<string, string>;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const TOKEN_TYPE_ICONS: Record<DesignTokenType, React.ComponentType<{ className?: string }>> = {
  animation: Play,
  border: LinkIcon,
  breakpoint: Maximize,
  color: Palette,
  custom: Code,
  opacity: Eye,
  radius: AlertCircle,
  shadow: Zap,
  spacing: Hash,
  typography: FileCode,
  'z-index': Layers,
};

const TOKEN_TYPE_LABELS: Record<DesignTokenType, string> = {
  animation: 'Animation',
  border: 'Borders',
  breakpoint: 'Breakpoints',
  color: 'Colors',
  custom: 'Custom',
  opacity: 'Opacity',
  radius: 'Border Radius',
  shadow: 'Shadows',
  spacing: 'Spacing',
  typography: 'Typography',
  'z-index': 'Z-Index',
};

const TOKEN_TYPE_COLORS: Record<DesignTokenType, string> = {
  animation: 'hsl(var(--red-500))',
  border: 'hsl(var(--orange-500))',
  breakpoint: 'hsl(var(--indigo-500))',
  color: 'hsl(var(--primary))',
  custom: 'hsl(var(--slate-500))',
  opacity: 'hsl(var(--yellow-500))',
  radius: 'hsl(var(--pink-500))',
  shadow: 'hsl(var(--purple-500))',
  spacing: 'hsl(var(--green-500))',
  typography: 'hsl(var(--blue-500))',
  'z-index': 'hsl(var(--cyan-500))',
};

// =============================================================================
// COMPONENT
// =============================================================================

function DesignTokenBrowserComponent({
  tokens,
  onSelectToken,
  selectedTokenId,
  onLinkToFigma,
  showComponentUsage = true,
  componentMap = new Map(),
}: DesignTokenBrowserProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [copiedTokenId, setCopiedTokenId] = useState<string | null>(null);

  // Filter and group tokens
  const { filteredTokens, groupedByType, stats } = useMemo(() => {
    let filtered = tokens;

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.path.some((p) => p.toLowerCase().includes(query)) ||
          (t.description?.toLowerCase().includes(query) ?? t.value.toLowerCase().includes(query)) ||
          t.tags?.some((tag) => tag.toLowerCase().includes(query)),
      );
    }

    // Group by type
    const grouped = new Map<DesignTokenType, DesignToken[]>();
    for (const token of filtered) {
      const { type } = token;
      if (!grouped.has(type)) {
        grouped.set(type, []);
      }
      grouped.get(type)!.push(token);
    }

    // Sort within each category
    for (const [, list] of grouped) {
      list.sort((a, b) => a.name.localeCompare(b.name));
    }

    // Stats
    const stats = {
      total: tokens.length,
      withFigmaStyle: tokens.filter((t) => t.figmaStyleId).length,
      withReferences: tokens.filter((t) => t.referencesTokenId ?? t.referencedByIds?.length).length,
      withUsage: tokens.filter((t) => t.usageCount > 0).length,
    };

    return { filteredTokens: filtered, groupedByType: grouped, stats };
  }, [tokens, searchQuery]);

  // Handle category toggle
  const toggleCategory = useCallback((category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  }, []);

  const expandAllCategories = useCallback(() => {
    const allCategories = new Set([...groupedByType.keys()] as string[]);
    setExpandedCategories(allCategories);
  }, [groupedByType]);

  const collapseAllCategories = useCallback(() => {
    setExpandedCategories(new Set());
  }, []);

  const copyToClipboard = useCallback((text: string, tokenId: string) => {
    if (typeof globalThis !== 'undefined' && 'navigator' in globalThis) {
      const clipboard = globalThis.navigator?.clipboard;
      if (clipboard) {
        void clipboard.writeText(text);
      }
    }
    setCopiedTokenId(tokenId);
    globalThis.setTimeout(() => {
      setCopiedTokenId(null);
    }, 1500);
  }, []);

  if (tokens.length === 0) {
    return (
      <Card className='h-full'>
        <CardContent className='flex h-full items-center justify-center'>
          <div className='text-muted-foreground py-12 text-center'>
            <Palette className='mx-auto mb-3 h-12 w-12 opacity-50' />
            <p className='text-sm font-medium'>No design tokens</p>
            <p className='mx-auto mt-1 max-w-xs text-xs'>
              Import tokens from Figma, Tokens Studio, or define them manually
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <TooltipProvider>
      <Card className='flex h-full flex-col overflow-hidden'>
        {/* Header */}
        <CardHeader className='border-b px-4 py-3'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-2'>
              <Palette className='h-5 w-5 text-purple-500' />
              <CardTitle className='text-sm font-semibold'>Design Tokens</CardTitle>
            </div>
          </div>

          {/* Token stats */}
          <div className='text-muted-foreground mt-2 flex flex-wrap items-center gap-3 text-xs'>
            <span className='flex items-center gap-1'>
              <Palette className='h-3 w-3' />
              {stats.total} tokens
            </span>
            {stats.withUsage > 0 && (
              <span className='flex items-center gap-1'>
                <Code className='h-3 w-3' />
                {stats.withUsage} in use
              </span>
            )}
            {stats.withFigmaStyle > 0 && (
              <Tooltip delayDuration={200}>
                <TooltipTrigger>
                  <span className='flex items-center gap-1'>
                    <Figma className='h-3 w-3' />
                    {stats.withFigmaStyle} synced
                  </span>
                </TooltipTrigger>
                <TooltipContent>Linked to Figma styles</TooltipContent>
              </Tooltip>
            )}
            {stats.withReferences > 0 && (
              <Tooltip delayDuration={200}>
                <TooltipTrigger>
                  <span className='flex items-center gap-1'>
                    <LinkIcon className='h-3 w-3' />
                    {stats.withReferences} linked
                  </span>
                </TooltipTrigger>
                <TooltipContent>Reference other tokens</TooltipContent>
              </Tooltip>
            )}
          </div>
        </CardHeader>

        {/* Filter buttons row */}
        <div className='bg-muted/30 flex flex-wrap items-center gap-2 overflow-x-auto border-b px-4 py-2'>
          {[...groupedByType.keys()].map((type) => {
            const TypeIcon = TOKEN_TYPE_ICONS[type];
            return (
              <Button
                key={type}
                variant='ghost'
                size='sm'
                className='h-6 gap-1 px-2 text-xs whitespace-nowrap'
                onClick={() => {
                  toggleCategory(type);
                }}
              >
                {TypeIcon && <TypeIcon className='h-3 w-3' />}
                {TOKEN_TYPE_LABELS[type]} ({groupedByType.get(type)?.length ?? 0})
              </Button>
            );
          })}
        </div>

        {/* Search */}
        <div className='border-b px-4 py-2'>
          <div className='relative'>
            <Search className='text-muted-foreground absolute top-2 left-2.5 h-4 w-4' />
            <Input
              placeholder='Search tokens by name, value, or path...'
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
              }}
              className='h-8 pl-8 text-sm'
            />
          </div>
        </div>

        {/* Main content */}
        <ScrollArea className='flex-1 overflow-hidden'>
          <div className='p-2'>
            {/* Expand/Collapse controls */}
            <div className='mb-2 flex gap-2 px-2'>
              <Button
                variant='ghost'
                size='sm'
                className='h-6 px-2 text-xs'
                onClick={expandAllCategories}
              >
                Expand All
              </Button>
              <Button
                variant='ghost'
                size='sm'
                className='h-6 px-2 text-xs'
                onClick={collapseAllCategories}
              >
                Collapse All
              </Button>
            </div>

            {/* Token categories */}
            {filteredTokens.length > 0 ? (
              [...groupedByType.entries()].map(([type, typeTokens]) => (
                <TokenCategorySection
                  key={type}
                  type={type}
                  tokens={typeTokens}
                  isExpanded={expandedCategories.has(type)}
                  onToggle={() => {
                    toggleCategory(type);
                  }}
                  selectedTokenId={selectedTokenId}
                  onSelectToken={onSelectToken}
                  onLinkToFigma={onLinkToFigma}
                  onCopyValue={(value, tokenId) => {
                    copyToClipboard(value, tokenId);
                  }}
                  copiedTokenId={copiedTokenId}
                  showComponentUsage={showComponentUsage}
                  componentMap={componentMap}
                />
              ))
            ) : (
              <div className='text-muted-foreground py-8 text-center'>
                <Search className='mx-auto mb-2 h-8 w-8 opacity-50' />
                <p className='text-sm'>No tokens found</p>
                <p className='mt-1 text-xs'>Try a different search term</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </Card>
    </TooltipProvider>
  );
}

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

interface TokenCategorySectionProps {
  type: DesignTokenType;
  tokens: DesignToken[];
  isExpanded: boolean;
  onToggle: () => void;
  selectedTokenId: string | null | undefined;
  onSelectToken: ((tokenId: string) => void) | undefined;
  onLinkToFigma: ((tokenId: string) => void) | undefined;
  onCopyValue: (value: string, tokenId: string) => void;
  copiedTokenId: string | null | undefined;
  showComponentUsage: boolean;
  componentMap: Map<string, string> | undefined;
}

function TokenCategorySection({
  type,
  tokens,
  isExpanded,
  onToggle,
  selectedTokenId,
  onSelectToken,
  onLinkToFigma,
  onCopyValue,
  copiedTokenId,
  showComponentUsage = true,
  componentMap = new Map(),
}: TokenCategorySectionProps) {
  const IconComponent = TOKEN_TYPE_ICONS[type] || Code;
  const label = TOKEN_TYPE_LABELS[type];
  const iconColor = TOKEN_TYPE_COLORS[type];
  const iconStyle = useMemo(() => ({ color: iconColor }), [iconColor]);

  return (
    <Collapsible open={isExpanded} onOpenChange={onToggle}>
      <CollapsibleTrigger>
        <Button variant='ghost' className='mb-1 h-8 w-full justify-start gap-2 px-2'>
          {isExpanded ? (
            <ChevronDown className='h-3.5 w-3.5' />
          ) : (
            <ChevronRight className='h-3.5 w-3.5' />
          )}
          <div style={iconStyle}>
            <IconComponent className='h-3.5 w-3.5' />
          </div>
          <span className='text-sm font-medium'>{label}</span>
          <Badge variant='secondary' className='ml-auto text-xs'>
            {tokens.length}
          </Badge>
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className='mb-2 space-y-1 pl-6'>
          {tokens.map((token) => (
            <TokenListItem
              key={token.id}
              token={token}
              isSelected={selectedTokenId === token.id}
              onSelect={() => onSelectToken?.(token.id)}
              onLinkToFigma={
                onLinkToFigma
                  ? () => {
                      onLinkToFigma(token.id);
                    }
                  : undefined
              }
              onCopyValue={(value) => {
                onCopyValue(value, token.id);
              }}
              isCopied={copiedTokenId === token.id}
              showComponentUsage={showComponentUsage}
              componentMap={componentMap}
            />
          ))}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

interface TokenListItemProps {
  token: DesignToken;
  isSelected: boolean;
  onSelect: () => void;
  onLinkToFigma: (() => void) | undefined;
  onCopyValue: (value: string) => void;
  isCopied: boolean;
  showComponentUsage?: boolean;
  componentMap?: Map<string, string>;
}

function TokenListItem({
  token,
  isSelected,
  onSelect,
  onLinkToFigma,
  onCopyValue,
  isCopied,
  showComponentUsage = true,
  componentMap = new Map(),
}: TokenListItemProps) {
  const [expandDetails, setExpandDetails] = useState(false);
  const hasReferences = token.referencesTokenId ?? token.referencedByIds?.length;
  const hasUsage = token.usageCount > 0;

  return (
    <div
      className={`group flex cursor-pointer flex-col rounded-md border transition-colors ${isSelected ? 'bg-primary/10 border-primary/30' : 'hover:bg-muted/50 border-muted'} `}
    >
      {/* Main row */}
      <div
        className='flex items-center gap-2 p-2'
        onClick={onSelect}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onSelect();
          }
        }}
        role='button'
        tabIndex={0}
      >
        {/* Token preview */}
        <TokenPreview token={token} />

        {/* Token info */}
        <div className='min-w-0 flex-1'>
          <div className='mb-0.5 flex items-center gap-1.5'>
            <code className='truncate font-mono text-xs font-semibold'>{token.name}</code>
            {token.figmaStyleId && (
              <Tooltip delayDuration={200}>
                <TooltipTrigger>
                  <Figma className='h-3 w-3 shrink-0 text-blue-500' />
                </TooltipTrigger>
                <TooltipContent>Linked to Figma</TooltipContent>
              </Tooltip>
            )}
            {hasReferences && (
              <Tooltip delayDuration={200}>
                <TooltipTrigger>
                  <LinkIcon className='h-3 w-3 shrink-0 text-amber-500' />
                </TooltipTrigger>
                <TooltipContent>References other tokens</TooltipContent>
              </Tooltip>
            )}
          </div>

          {/* Path breadcrumb */}
          <div className='mb-0.5 flex items-center gap-1'>
            <span className='text-muted-foreground text-[10px]'>{token.path.join(' / ')}</span>
          </div>

          {/* Value display */}
          <div className='flex items-center gap-2'>
            <code className='text-muted-foreground bg-muted truncate rounded px-1.5 py-0.5 font-mono text-[10px]'>
              {token.resolvedValue ?? token.value}
            </code>
          </div>
        </div>

        {/* Actions */}
        <div className='flex shrink-0 items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100'>
          {/* Copy value */}
          <Tooltip delayDuration={200}>
            <TooltipTrigger asChild>
              <Button
                variant='ghost'
                size='sm'
                className='h-6 w-6 p-0'
                onClick={(e) => {
                  e.stopPropagation();
                  onCopyValue(token.resolvedValue ?? token.value);
                }}
              >
                <Copy
                  className={`h-3.5 w-3.5 transition-colors ${isCopied ? 'text-green-500' : ''}`}
                />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{isCopied ? 'Copied!' : 'Copy value'}</TooltipContent>
          </Tooltip>

          {/* Link to Figma */}
          {onLinkToFigma && !token.figmaStyleId && (
            <Tooltip delayDuration={200}>
              <TooltipTrigger asChild>
                <Button
                  variant='ghost'
                  size='sm'
                  className='h-6 w-6 p-0'
                  onClick={(e) => {
                    e.stopPropagation();
                    onLinkToFigma();
                  }}
                >
                  <Figma className='h-3.5 w-3.5' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Link to Figma style</TooltipContent>
            </Tooltip>
          )}

          {/* Expand details */}
          {(hasUsage || (hasReferences ?? token.description)) && (
            <Button
              variant='ghost'
              size='sm'
              className='h-6 w-6 p-0'
              onClick={(e) => {
                e.stopPropagation();
                setExpandDetails(!expandDetails);
              }}
            >
              <ChevronDown
                className={`h-3.5 w-3.5 transition-transform ${expandDetails ? 'rotate-180' : ''}`}
              />
            </Button>
          )}
        </div>

        {/* Usage badge */}
        {hasUsage && (
          <Tooltip delayDuration={200}>
            <TooltipTrigger>
              <Badge variant='secondary' className='shrink-0 px-1.5 text-[10px]'>
                {token.usageCount}
              </Badge>
            </TooltipTrigger>
            <TooltipContent>Used {token.usageCount} times</TooltipContent>
          </Tooltip>
        )}
      </div>

      {/* Expandable details */}
      {expandDetails && (
        <>
          <Separator className='mx-2' />
          <div className='space-y-2 p-2'>
            {/* Description */}
            {token.description && (
              <div>
                <p className='text-muted-foreground mb-1 text-[10px] font-medium'>Description</p>
                <p className='text-foreground text-xs'>{token.description}</p>
              </div>
            )}

            {/* Referenced token */}
            {token.referencesTokenId && (
              <div>
                <p className='text-muted-foreground mb-1 text-[10px] font-medium'>References</p>
                <code className='bg-muted block rounded px-2 py-1 font-mono text-[10px]'>
                  ${token.referencesTokenId}
                </code>
              </div>
            )}

            {/* Referenced by tokens */}
            {token.referencedByIds && token.referencedByIds.length > 0 && (
              <div>
                <p className='text-muted-foreground mb-1 text-[10px] font-medium'>
                  Referenced by {token.referencedByIds.length} token(s)
                </p>
                <div className='flex flex-wrap gap-1'>
                  {token.referencedByIds.slice(0, 3).map((id) => (
                    <Badge key={id} variant='outline' className='text-[10px]'>
                      {id}
                    </Badge>
                  ))}
                  {token.referencedByIds.length > 3 && (
                    <Badge variant='outline' className='text-[10px]'>
                      +{token.referencedByIds.length - 3}
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* Component usage */}
            {showComponentUsage &&
              token.usedByComponentIds &&
              token.usedByComponentIds.length > 0 && (
                <div>
                  <p className='text-muted-foreground mb-1 text-[10px] font-medium'>
                    Used in {token.usedByComponentIds.length} component(s)
                  </p>
                  <div className='flex flex-wrap gap-1'>
                    {token.usedByComponentIds.slice(0, 3).map((componentId) => (
                      <Badge key={componentId} variant='outline' className='text-[10px]'>
                        {componentMap.get(componentId) ?? componentId}
                      </Badge>
                    ))}
                    {token.usedByComponentIds.length > 3 && (
                      <Badge variant='outline' className='text-[10px]'>
                        +{token.usedByComponentIds.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>
              )}

            {/* Figma sync info */}
            {token.figmaStyleId && (
              <div className='flex items-center gap-2 border-t pt-1'>
                <Figma className='h-3.5 w-3.5 text-blue-500' />
                <a
                  href='https://figma.com/file/styles'
                  target='_blank'
                  rel='noopener noreferrer'
                  className='flex items-center gap-1 text-[10px] text-blue-500 hover:text-blue-600'
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                >
                  View in Figma
                  <ExternalLink className='h-2.5 w-2.5' />
                </a>
              </div>
            )}

            {/* Tags */}
            {token.tags && token.tags.length > 0 && (
              <div className='flex flex-wrap gap-1 border-t pt-1'>
                {token.tags.slice(0, 3).map((tag) => (
                  <Badge key={tag} variant='secondary' className='text-[10px]'>
                    {tag}
                  </Badge>
                ))}
                {token.tags.length > 3 && (
                  <Badge variant='secondary' className='text-[10px]'>
                    +{token.tags.length - 3}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

interface TokenPreviewProps {
  token: DesignToken;
}

const colorPreviewStyle = (value: string): CSSProperties => ({
  backgroundColor: value,
});
const shadowPreviewStyle = (value: string): CSSProperties => ({
  boxShadow: value,
});
const borderPreviewStyle = (radius: string): CSSProperties => ({
  borderColor: 'currentColor',
  borderRadius: radius,
});

function TokenPreview({ token }: TokenPreviewProps) {
  const value = token.resolvedValue ?? token.value;
  switch (token.type) {
    case 'color': {
      return (
        <div
          className='border-muted h-8 w-8 shrink-0 rounded-md border-2'
          style={colorPreviewStyle(value)}
          title={value}
        />
      );
    }

    case 'shadow': {
      return (
        <div
          className='border-muted h-8 w-8 shrink-0 rounded-md border'
          style={shadowPreviewStyle(value)}
        />
      );
    }

    case 'border':
    case 'radius': {
      return (
        <div
          className='h-8 w-8 shrink-0 rounded border-2'
          style={borderPreviewStyle(token.type === 'radius' ? value : '4px')}
        />
      );
    }
    default: {
      return (
        <div className='border-muted bg-muted flex h-8 w-8 shrink-0 items-center justify-center rounded border'>
          <Code className='text-muted-foreground h-4 w-4' />
        </div>
      );
    }
  }
}

// =============================================================================
// EXPORTS
// =============================================================================

export const DesignTokenBrowser = memo(DesignTokenBrowserComponent);
