// Node Detail Panel - Rich information display for selected nodes

import {
  ArrowDownRight,
  ArrowUpRight,
  ChevronRight,
  Circle,
  Code,
  ExternalLink,
  FileText,
  GitBranch,
  Image,
  Link2,
  User,
  X,
} from 'lucide-react';
import { memo } from 'react';

import type { Item, Link } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import { Separator } from '@tracertm/ui/components/Separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui/components/Tabs';

import type { EnhancedNodeData } from './types';

import { ENHANCED_TYPE_COLORS, LINK_STYLES } from './types';

interface NodeDetailPanelProps {
  node: EnhancedNodeData | null;
  relatedItems: Item[];
  incomingLinks: Link[];
  outgoingLinks: Link[];
  onClose: () => void;
  onNavigateToItem: (itemId: string) => void;
  onFocusNode: (nodeId: string) => void;
}

function NodeDetailPanelComponent({
  node,
  relatedItems,
  incomingLinks,
  outgoingLinks,
  onClose,
  onNavigateToItem,
  onFocusNode,
}: NodeDetailPanelProps) {
  if (!node) {
    return null;
  }

  const bgColor = ENHANCED_TYPE_COLORS[node.type] ?? '#64748b';

  // Group links by type
  const incomingByType = incomingLinks.reduce<Record<string, Link[]>>((acc, link) => {
    const type = link.type || 'related_to';
    acc[type] ??= [];
    acc[type].push(link);
    return acc;
  }, {});

  const outgoingByType = outgoingLinks.reduce<Record<string, Link[]>>((acc, link) => {
    const type = link.type || 'related_to';
    acc[type] ??= [];
    acc[type].push(link);
    return acc;
  }, {});

  return (
    <Card
      className='flex h-full w-full max-w-[22rem] min-w-0 shrink-0 flex-col overflow-hidden border-l-4 sm:max-w-[24rem]'
      style={{ borderLeftColor: bgColor }}
    >
      {/* Header */}
      <div className='bg-muted/30 min-w-0 border-b p-2 sm:p-4'>
        <div className='flex min-w-0 items-start justify-between gap-2'>
          <div className='min-w-0 flex-1'>
            <div className='mb-1.5 flex flex-wrap items-center gap-1.5 sm:mb-2 sm:gap-2'>
              <Badge
                variant='outline'
                className='shrink-0 px-1.5 text-[10px] sm:px-2 sm:text-xs'
                style={{
                  backgroundColor: `${bgColor}20`,
                  borderColor: bgColor,
                  color: bgColor,
                }}
              >
                {node.type.replaceAll('_', ' ')}
              </Badge>
              <Badge variant='secondary' className='shrink-0 text-[10px] sm:text-xs'>
                {node.status}
              </Badge>
            </div>
            <h3 className='truncate text-sm leading-tight font-semibold sm:text-base md:text-lg'>
              {node.label}
            </h3>
          </div>
          <Button
            variant='ghost'
            size='sm'
            className='h-7 w-7 shrink-0 p-0 sm:h-8 sm:w-8'
            onClick={onClose}
          >
            <X className='h-3.5 w-3.5 sm:h-4 sm:w-4' />
          </Button>
        </div>

        {/* Quick stats */}
        <div className='text-muted-foreground mt-2 flex flex-wrap items-center gap-2 text-xs sm:mt-3 sm:gap-4 sm:text-sm'>
          <div className='flex items-center gap-1'>
            <ArrowDownRight className='h-4 w-4 text-green-500' />
            <span>{incomingLinks.length} incoming</span>
          </div>
          <div className='flex items-center gap-1'>
            <ArrowUpRight className='h-4 w-4 text-blue-500' />
            <span>{outgoingLinks.length} outgoing</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue='details' className='flex flex-1 flex-col overflow-hidden'>
        <TabsList className='w-full justify-start rounded-none border-b bg-transparent p-0'>
          <TabsTrigger
            value='details'
            className='data-[state=active]:border-primary rounded-none border-b-2 border-transparent text-xs data-[state=active]:bg-transparent sm:text-sm'
          >
            <FileText className='mr-1 h-3 w-3 shrink-0 sm:h-4 sm:w-4' />
            <span className='truncate'>Details</span>
          </TabsTrigger>
          <TabsTrigger
            value='links'
            className='data-[state=active]:border-primary rounded-none border-b-2 border-transparent text-xs data-[state=active]:bg-transparent sm:text-sm'
          >
            <Link2 className='mr-1 h-3 w-3 shrink-0 sm:h-4 sm:w-4' />
            <span className='truncate'>Links</span>
          </TabsTrigger>
          {node.uiPreview && (
            <TabsTrigger
              value='preview'
              className='data-[state=active]:border-primary rounded-none border-b-2 border-transparent text-xs data-[state=active]:bg-transparent sm:text-sm'
            >
              <Image className='mr-1 h-3 w-3 shrink-0 sm:h-4 sm:w-4' />
              <span className='truncate'>Preview</span>
            </TabsTrigger>
          )}
          <TabsTrigger
            value='code'
            className='data-[state=active]:border-primary rounded-none border-b-2 border-transparent text-xs data-[state=active]:bg-transparent sm:text-sm'
          >
            <Code className='mr-1 h-3 w-3 shrink-0 sm:h-4 sm:w-4' />
            <span className='truncate'>Code</span>
          </TabsTrigger>
        </TabsList>

        <ScrollArea className='flex-1'>
          {/* Details Tab */}
          <TabsContent value='details' className='m-0 space-y-4 p-4'>
            {/* Description */}
            <div className='min-w-0'>
              <h4 className='text-muted-foreground mb-1 text-xs font-medium sm:text-sm'>
                Description
              </h4>
              <p className='line-clamp-4 text-xs sm:text-sm md:line-clamp-none'>
                {node.item.description ?? 'No description provided'}
              </p>
            </div>

            <Separator />

            {/* Metadata */}
            <div className='grid grid-cols-2 gap-2 text-xs sm:gap-3 sm:text-sm'>
              {node.item.owner && (
                <div>
                  <span className='text-muted-foreground flex items-center gap-1'>
                    <User className='h-3 w-3' /> Owner
                  </span>
                  <p className='font-medium'>{node.item.owner}</p>
                </div>
              )}
              <div>
                <span className='text-muted-foreground'>Priority</span>
                <p className='font-medium capitalize'>{node.item.priority || '—'}</p>
              </div>
              <div>
                <span className='text-muted-foreground'>Version</span>
                <p className='font-medium'>{node.item.version || 1}</p>
              </div>
              <div>
                <span className='text-muted-foreground'>View</span>
                <p className='font-medium'>{node.item.view || '—'}</p>
              </div>
            </div>

            {/* Hierarchy */}
            {node.parentId && (
              <>
                <Separator />
                <div>
                  <h4 className='text-muted-foreground mb-2 flex items-center gap-1 text-sm font-medium'>
                    <GitBranch className='h-3 w-3' /> Hierarchy
                  </h4>
                  <Button
                    variant='outline'
                    size='sm'
                    className='w-full justify-start'
                    onClick={() => {
                      onFocusNode(node.parentId!);
                    }}
                  >
                    <ChevronRight className='mr-2 h-4 w-4 -rotate-90' />
                    Go to parent
                  </Button>
                </div>
              </>
            )}

            {/* Timestamps */}
            <Separator />
            <div className='text-muted-foreground space-y-1 text-xs'>
              <p>Created: {new Date(node.item.createdAt).toLocaleString()}</p>
              <p>Updated: {new Date(node.item.updatedAt).toLocaleString()}</p>
            </div>
          </TabsContent>

          {/* Links Tab */}
          <TabsContent value='links' className='m-0 space-y-4 p-4'>
            {/* Incoming Links */}
            <div>
              <h4 className='text-muted-foreground mb-2 flex items-center gap-1 text-sm font-medium'>
                <ArrowDownRight className='h-4 w-4 text-green-500' />
                Incoming ({incomingLinks.length})
              </h4>
              {Object.entries(incomingByType).length > 0 ? (
                <div className='space-y-3'>
                  {Object.entries(incomingByType).map(([type, links]) => (
                    <div key={type}>
                      <div className='mb-1.5 flex items-center gap-2'>
                        <div
                          className='h-1 w-6 rounded'
                          style={{
                            backgroundColor: LINK_STYLES[type]?.color ?? '#64748b',
                          }}
                        />
                        <span className='text-muted-foreground text-xs'>
                          {type.replaceAll('_', ' ')} ({links.length})
                        </span>
                      </div>
                      <div className='space-y-1 pl-4'>
                        {links.slice(0, 5).map((link) => {
                          const sourceItem = relatedItems.find((i) => i.id === link.sourceId);
                          return (
                            <Button
                              key={link.id}
                              variant='ghost'
                              size='sm'
                              className='h-7 w-full justify-start px-2 text-xs'
                              onClick={() => {
                                onFocusNode(link.sourceId);
                              }}
                            >
                              <Circle
                                className='mr-2 h-2 w-2'
                                style={{
                                  color: ENHANCED_TYPE_COLORS[sourceItem?.type ?? ''] ?? '#64748b',
                                  fill: ENHANCED_TYPE_COLORS[sourceItem?.type ?? ''] ?? '#64748b',
                                }}
                              />
                              <span className='truncate'>{sourceItem?.title ?? link.sourceId}</span>
                            </Button>
                          );
                        })}
                        {links.length > 5 && (
                          <p className='text-muted-foreground pl-2 text-xs'>
                            +{links.length - 5} more
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className='text-muted-foreground text-sm'>No incoming links</p>
              )}
            </div>

            <Separator />

            {/* Outgoing Links */}
            <div>
              <h4 className='text-muted-foreground mb-2 flex items-center gap-1 text-sm font-medium'>
                <ArrowUpRight className='h-4 w-4 text-blue-500' />
                Outgoing ({outgoingLinks.length})
              </h4>
              {Object.entries(outgoingByType).length > 0 ? (
                <div className='space-y-3'>
                  {Object.entries(outgoingByType).map(([type, links]) => (
                    <div key={type}>
                      <div className='mb-1.5 flex items-center gap-2'>
                        <div
                          className='h-1 w-6 rounded'
                          style={{
                            backgroundColor: LINK_STYLES[type]?.color ?? '#64748b',
                          }}
                        />
                        <span className='text-muted-foreground text-xs'>
                          {type.replaceAll('_', ' ')} ({links.length})
                        </span>
                      </div>
                      <div className='space-y-1 pl-4'>
                        {links.slice(0, 5).map((link) => {
                          const targetItem = relatedItems.find((i) => i.id === link.targetId);
                          return (
                            <Button
                              key={link.id}
                              variant='ghost'
                              size='sm'
                              className='h-7 w-full justify-start px-2 text-xs'
                              onClick={() => {
                                onFocusNode(link.targetId);
                              }}
                            >
                              <Circle
                                className='mr-2 h-2 w-2'
                                style={{
                                  color: ENHANCED_TYPE_COLORS[targetItem?.type ?? ''] ?? '#64748b',
                                  fill: ENHANCED_TYPE_COLORS[targetItem?.type ?? ''] ?? '#64748b',
                                }}
                              />
                              <span className='truncate'>{targetItem?.title ?? link.targetId}</span>
                            </Button>
                          );
                        })}
                        {links.length > 5 && (
                          <p className='text-muted-foreground pl-2 text-xs'>
                            +{links.length - 5} more
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className='text-muted-foreground text-sm'>No outgoing links</p>
              )}
            </div>
          </TabsContent>

          {/* Preview Tab */}
          {node.uiPreview && (
            <TabsContent value='preview' className='m-0 space-y-4 p-4'>
              {node.uiPreview.screenshotUrl ? (
                <div className='space-y-3'>
                  <img
                    src={node.uiPreview.screenshotUrl}
                    alt={`Preview of ${node.label}`}
                    className='w-full rounded-lg border shadow-sm'
                  />
                  {node.uiPreview.interactiveWidgetUrl && (
                    <a
                      href={node.uiPreview.interactiveWidgetUrl}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='border-input bg-background hover:bg-accent hover:text-accent-foreground flex h-9 w-full items-center justify-center gap-2 rounded-md border px-3 text-sm font-medium'
                    >
                      <ExternalLink className='h-4 w-4' />
                      Open Interactive Preview
                    </a>
                  )}
                </div>
              ) : (
                <div className='text-muted-foreground py-8 text-center'>
                  <Image className='mx-auto mb-2 h-12 w-12 opacity-50' />
                  <p className='text-sm'>No preview available</p>
                </div>
              )}
            </TabsContent>
          )}

          {/* Code Tab */}
          <TabsContent value='code' className='m-0 space-y-4 p-4'>
            {node.uiPreview?.componentCode ? (
              <div className='space-y-2'>
                <h4 className='text-muted-foreground text-sm font-medium'>Component Code</h4>
                <pre className='bg-muted overflow-x-auto rounded-lg p-3 text-xs'>
                  <code>{node.uiPreview.componentCode}</code>
                </pre>
              </div>
            ) : (
              <div className='text-muted-foreground py-8 text-center'>
                <Code className='mx-auto mb-2 h-12 w-12 opacity-50' />
                <p className='text-sm'>No code linked to this item</p>
                <p className='mt-1 text-xs'>Link code items to see them here</p>
              </div>
            )}
          </TabsContent>
        </ScrollArea>
      </Tabs>

      {/* Actions Footer */}
      <div className='bg-muted/30 flex gap-2 border-t p-3'>
        <Button
          variant='outline'
          size='sm'
          className='flex-1'
          onClick={() => {
            onNavigateToItem(node.id);
          }}
        >
          <ExternalLink className='mr-2 h-4 w-4' />
          Open Details
        </Button>
      </div>
    </Card>
  );
}

export const NodeDetailPanel = memo(NodeDetailPanelComponent);
