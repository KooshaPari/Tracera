'use client';

/**
 * Instant Search Component
 *
 * High-performance search UI with:
 * - Web worker background processing
 * - Virtual scrolling for large result sets
 * - Match highlighting
 * - Keyboard navigation
 * - <100ms response time
 */

import type { JSX } from 'react';

import { useVirtualizer } from '@tanstack/react-virtual';
import { useCallback, useEffect, useRef, useState } from 'react';

import { formatSearchPreview } from '../lib/search-config';
import { useSearchWorker } from '../lib/use-search-worker';

interface InstantSearchProps {
  isOpen: boolean;
  onClose: () => void;
  placeholder?: string;
  maxResults?: number;
}

export function InstantSearch({
  isOpen,
  onClose,
  placeholder = 'Search documentation...',
  maxResults = 20,
}: InstantSearchProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsContainerRef = useRef<HTMLDivElement>(null);

  const { search, results, isReady, isSearching, error, performance } = useSearchWorker();

  // Perform search on query change
  useEffect(() => {
    if (query.length >= 2) {
      search(query, maxResults);
    }
  }, [query, search, maxResults]);

  // Reset selection when results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [results]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Virtual scrolling for results
  const rowVirtualizer = useVirtualizer({
    count: results.length,
    estimateSize: () => 80,
    getScrollElement: () => resultsContainerRef.current,
    overscan: 5,
  });

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
          break;
        }

        case 'ArrowUp': {
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        }

        case 'Enter': {
          e.preventDefault();
          if (results[selectedIndex]) {
            window.location.href = results[selectedIndex].item.url;
          }
          break;
        }

        case 'Escape': {
          e.preventDefault();
          onClose();
          break;
        }
      }
    },
    [results, selectedIndex, onClose],
  );

  /**
   * Highlight matched text
   */
  const highlightMatches = useCallback(
    (text: string, matches?: readonly { indices: readonly [number, number][] }[]) => {
      if (!matches || matches.length === 0) {
        return <span>{text}</span>;
      }

      const indices = matches[0]?.indices || [];
      const parts: JSX.Element[] = [];
      let lastIndex = 0;

      indices.forEach(([start, end], i) => {
        // Add text before match
        if (start > lastIndex) {
          parts.push(<span key={`text-${i}`}>{text.slice(lastIndex, start)}</span>);
        }

        // Add highlighted match
        parts.push(
          <mark key={`match-${i}`} className='bg-yellow-200 dark:bg-yellow-800'>
            {text.slice(start, end + 1)}
          </mark>,
        );

        lastIndex = end + 1;
      });

      // Add remaining text
      if (lastIndex < text.length) {
        parts.push(<span key='text-end'>{text.slice(lastIndex)}</span>);
      }

      return <>{parts}</>;
    },
    [],
  );

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className='fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[20vh]'
      onClick={onClose}
    >
      <div
        className='w-full max-w-2xl rounded-lg border border-gray-200 bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-800'
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className='border-b border-gray-200 p-4 dark:border-gray-700'>
          <input
            ref={inputRef}
            type='text'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className='w-full bg-transparent text-lg outline-none'
            aria-label='Search'
            aria-autocomplete='list'
            aria-controls='search-results'
            aria-activedescendant={`result-${selectedIndex}`}
          />

          {/* Status */}
          <div className='mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400'>
            {!isReady && <span>Loading search index...</span>}
            {isSearching && <span>Searching...</span>}
            {!isSearching && results.length > 0 && (
              <>
                <span>
                  {results.length} result{results.length !== 1 ? 's' : ''}
                </span>
                {performance.searchDuration && (
                  <span
                    className={
                      performance.searchDuration < 100
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-orange-600 dark:text-orange-400'
                    }
                  >
                    {performance.searchDuration.toFixed(0)}ms
                  </span>
                )}
              </>
            )}
            {error && <span className='text-red-500'>{error}</span>}
          </div>
        </div>

        {/* Results */}
        <div
          ref={resultsContainerRef}
          id='search-results'
          role='listbox'
          className='max-h-[50vh] overflow-auto'
        >
          {query.length < 2 ? (
            <div className='p-8 text-center text-sm text-gray-500 dark:text-gray-400'>
              Type at least 2 characters to search
            </div>
          ) : results.length === 0 && !isSearching ? (
            <div className='p-8 text-center text-sm text-gray-500 dark:text-gray-400'>
              No results found for &quot;{query}&quot;
            </div>
          ) : (
            <div
              style={{
                height: `${rowVirtualizer.getTotalSize()}px`,
                position: 'relative',
                width: '100%',
              }}
            >
              {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                const result = results[virtualRow.index];
                if (!result) return null;
                const isSelected = virtualRow.index === selectedIndex;

                return (
                  <a
                    key={virtualRow.key}
                    id={`result-${virtualRow.index}`}
                    href={result.item.url}
                    role='option'
                    aria-selected={isSelected}
                    className={`absolute left-0 top-0 w-full border-b border-gray-100 p-4 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-700/50 ${
                      isSelected ? 'bg-gray-50 dark:bg-gray-700/50' : ''
                    }`}
                    style={{
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                    onClick={() => onClose()}
                  >
                    {/* Title */}
                    <div className='font-medium text-gray-900 dark:text-gray-100'>
                      {highlightMatches(
                        result.item.title,
                        result.matches?.filter((m) => m.key === 'title'),
                      )}
                    </div>

                    {/* Description or Content Preview */}
                    <div className='mt-1 text-sm text-gray-600 dark:text-gray-400'>
                      {result.item.description
                        ? highlightMatches(
                            result.item.description,
                            result.matches?.filter((m) => m.key === 'description'),
                          )
                        : formatSearchPreview(result.item.content, query)}
                    </div>

                    {/* URL */}
                    <div className='mt-1 text-xs text-gray-500 dark:text-gray-500'>
                      {result.item.url}
                    </div>

                    {/* Score (debug) */}
                    {result.score !== undefined && (
                      <div className='mt-1 text-xs text-gray-400'>
                        Score: {(1 - result.score).toFixed(3)}
                      </div>
                    )}
                  </a>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className='border-t border-gray-200 p-3 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400'>
          <div className='flex items-center justify-between'>
            <div className='flex gap-4'>
              <span>
                <kbd className='rounded border border-gray-300 px-1.5 py-0.5 dark:border-gray-600'>
                  ↑↓
                </kbd>{' '}
                Navigate
              </span>
              <span>
                <kbd className='rounded border border-gray-300 px-1.5 py-0.5 dark:border-gray-600'>
                  ↵
                </kbd>{' '}
                Select
              </span>
              <span>
                <kbd className='rounded border border-gray-300 px-1.5 py-0.5 dark:border-gray-600'>
                  ESC
                </kbd>{' '}
                Close
              </span>
            </div>
            <span>Powered by Fuse.js</span>
          </div>
        </div>
      </div>
    </div>
  );
}
