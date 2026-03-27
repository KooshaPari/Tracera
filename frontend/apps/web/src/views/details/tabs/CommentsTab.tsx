/**
 * CommentsTab - Displays comments and discussions
 *
 * Shows:
 * - Comment thread
 * - User avatars and timestamps
 * - Reply functionality
 * - Comment metadata
 */

import { MessageSquare, Send, User } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import type { TypedItem } from '@tracertm/types';

import { cn } from '@/lib/utils';
import { Badge, Button, Card, Textarea } from '@tracertm/ui';

export interface CommentsTabProps {
  /** The item to display comments for */
  item: TypedItem;

  /** Optional CSS classes */
  className?: string;
}

interface Comment {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  edited?: boolean;
}

/**
 * CommentsTab displays comments and discussions for an item.
 * Note: This is a placeholder implementation. Real comment data
 * would come from the backend.
 */
function getInitials(name: string) {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60_000);
  const diffHours = Math.floor(diffMs / 3_600_000);
  const diffDays = Math.floor(diffMs / 86_400_000);

  if (diffMins < 1) {
    return 'Just now';
  }
  if (diffMins < 60) {
    return `${diffMins}m ago`;
  }
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }

  return date.toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

export function CommentsTab({ item, className }: CommentsTabProps) {
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Placeholder comments - in real implementation, these would come from the API
  const comments: Comment[] = [];

  const handleSubmit = async () => {
    if (!newComment.trim()) {
      toast.error('Comment cannot be empty');
      return;
    }

    setIsSubmitting(true);
    try {
      // tracked: https://github.com/KooshaPari/trace/issues/227
      await new Promise((resolve) => setTimeout(resolve, 500));
      toast.success('Comment added successfully');
      setNewComment('');
    } catch {
      toast.error('Failed to add comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={cn('space-y-6', className)} data-item-id={item.id}>
      {/* Comment Input */}
      <Card className='bg-muted/40 border-0 p-4'>
        <div className='space-y-4'>
          <div className='flex items-center gap-2'>
            <MessageSquare className='text-primary h-4 w-4' aria-hidden='true' />
            <h3 className='text-sm font-black tracking-widest uppercase'>Add Comment</h3>
          </div>

          <div className='flex gap-3'>
            <div className='bg-primary/10 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full'>
              <User className='text-primary h-4 w-4' aria-hidden='true' />
            </div>

            <div className='flex-1 space-y-3'>
              <Textarea
                value={newComment}
                onChange={(e) => {
                  setNewComment(e.target.value);
                }}
                placeholder='Write a comment...'
                className='min-h-[100px] resize-none'
                disabled={isSubmitting}
                aria-label='New comment'
              />

              <div className='flex justify-end'>
                <Button
                  onClick={handleSubmit}
                  disabled={!newComment.trim() || isSubmitting}
                  className='gap-2'
                  aria-label='Submit comment'
                >
                  {isSubmitting ? (
                    <>
                      <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className='h-4 w-4' aria-hidden='true' />
                      Comment
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Comments List */}
      <div className='space-y-4'>
        <div className='flex items-center gap-2'>
          <h2 className='text-lg font-black tracking-tight'>Discussion</h2>
          <Badge variant='secondary' className='text-xs'>
            {comments.length}
          </Badge>
        </div>

        {comments.length > 0 ? (
          <div className='space-y-4' role='list' aria-label='Comments'>
            {comments.map((comment) => (
              <Card key={comment.id} className='bg-muted/40 border-0 p-4' role='listitem'>
                <div className='flex gap-3'>
                  <div className='bg-primary/20 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full'>
                    <span className='text-primary text-xs font-black'>
                      {getInitials(comment.author)}
                    </span>
                  </div>

                  <div className='flex-1 space-y-2'>
                    <div className='flex flex-wrap items-center gap-2'>
                      <span className='text-sm font-bold'>{comment.author}</span>
                      <span className='text-muted-foreground text-xs'>
                        {formatTimestamp(comment.timestamp)}
                      </span>
                      {comment.edited && (
                        <Badge variant='outline' className='text-xs'>
                          Edited
                        </Badge>
                      )}
                    </div>

                    <p className='text-sm leading-relaxed whitespace-pre-wrap'>{comment.content}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className='bg-muted/40 border-0 p-8'>
            <div className='text-muted-foreground flex flex-col items-center justify-center'>
              <MessageSquare className='mb-3 h-12 w-12 opacity-20' aria-hidden='true' />
              <p className='text-sm font-medium'>No comments yet</p>
              <p className='text-xs'>Be the first to start the discussion</p>
            </div>
          </Card>
        )}
      </div>

      {/* Discussion Guidelines */}
      <Card className='bg-primary/5 border-0 p-4'>
        <div className='space-y-2'>
          <p className='text-primary text-xs font-black tracking-widest uppercase'>
            Discussion Guidelines
          </p>
          <ul className='text-muted-foreground space-y-1 text-xs'>
            <li className='flex items-start gap-2'>
              <span className='text-primary mt-0.5'>•</span>
              <span>Keep comments relevant to this item</span>
            </li>
            <li className='flex items-start gap-2'>
              <span className='text-primary mt-0.5'>•</span>
              <span>Be respectful and constructive</span>
            </li>
            <li className='flex items-start gap-2'>
              <span className='text-primary mt-0.5'>•</span>
              <span>Use @mentions to notify team members</span>
            </li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
