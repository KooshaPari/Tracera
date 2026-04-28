import { ArrowUp, Check, Edit2, Plus, X } from 'lucide-react';
import { useState } from 'react';

import type { ADROption } from '@tracertm/types';

import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

interface DecisionMatrixProps {
  options: ADROption[];
  onOptionEdit?: (option: ADROption) => void;
  onOptionAdd?: () => void;
  onOptionRemove?: (optionId: string) => void;
  className?: string;
  editable?: boolean;
  showScoring?: boolean;
}

function calculateScore(option: ADROption): number {
  const prosCount = option.pros?.length ?? 0;
  const consCount = option.cons?.length ?? 0;
  return Math.max(0, (prosCount - consCount) * 10);
}

export function DecisionMatrix({
  options,
  onOptionEdit,
  onOptionAdd,
  onOptionRemove,
  className,
  editable = false,
  showScoring = false,
}: DecisionMatrixProps) {
  const [sortBy, setSortBy] = useState<'chosen' | 'pros' | 'cons'>('chosen');

  if (!options || options.length === 0) {
    return (
      <Card className={className}>
        <CardContent className='flex h-40 items-center justify-center'>
          <div className='text-muted-foreground text-center'>
            <Plus className='mx-auto mb-2 h-8 w-8 opacity-20' />
            <p className='text-sm'>No options considered yet</p>
            {editable && onOptionAdd && (
              <Button variant='outline' size='sm' className='mt-3 gap-1' onClick={onOptionAdd}>
                <Plus className='h-3 w-3' />
                Add Option
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Sort options
  const sortedOptions = [...options].toSorted((a, b) => {
    switch (sortBy) {
      case 'chosen': {
        return a.isChosen ? -1 : b.isChosen ? 1 : 0;
      }
      case 'pros': {
        return (b.pros?.length ?? 0) - (a.pros?.length ?? 0);
      }
      case 'cons': {
        return (a.cons?.length ?? 0) - (b.cons?.length ?? 0);
      }
      default: {
        return 0;
      }
    }
  });

  return (
    <Card className={className}>
      <CardHeader className='flex flex-row items-center justify-between pb-3'>
        <CardTitle className='text-muted-foreground text-sm font-medium tracking-wider uppercase'>
          Considered Options
        </CardTitle>
        <div className='flex items-center gap-2'>
          <span className='text-muted-foreground text-xs'>Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => {
              setSortBy(e.target.value as typeof sortBy);
            }}
            className='border-border bg-background rounded border px-2 py-1 text-xs'
          >
            <option value='chosen'>Chosen First</option>
            <option value='pros'>Most Pros</option>
            <option value='cons'>Fewest Cons</option>
          </select>
          {editable && onOptionAdd && (
            <Button
              variant='outline'
              size='sm'
              className='ml-2 h-7 gap-1 text-xs'
              onClick={onOptionAdd}
            >
              <Plus className='h-3 w-3' />
              Add
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className='overflow-x-auto'>
        <table className='w-full text-sm'>
          <thead>
            <tr className='border-border border-b'>
              <th className='w-[25%] p-3 text-left font-semibold'>Option</th>
              <th className='w-[25%] p-3 text-left font-semibold'>Pros</th>
              <th className='w-[25%] p-3 text-left font-semibold'>Cons</th>
              {showScoring && <th className='w-[15%] p-3 text-right font-semibold'>Score</th>}
              {editable && <th className='w-[10%] p-3 text-right font-semibold'>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {sortedOptions.map((option) => (
              <tr
                key={option.id}
                className={`border-border/50 hover:bg-muted/30 border-b transition-colors ${
                  option.isChosen ? 'bg-primary/5 border-l-primary border-l-2' : ''
                }`}
              >
                {/* Option Name */}
                <td className='p-3 align-top'>
                  <div className='flex items-start gap-2'>
                    {option.isChosen && (
                      <ArrowUp className='text-primary mt-0.5 h-4 w-4 shrink-0' />
                    )}
                    <div>
                      <div className='flex items-center gap-2'>
                        <span className='font-semibold'>{option.title}</span>
                        {option.isChosen && (
                          <Badge variant='default' className='h-5 gap-1 px-1.5 text-[10px]'>
                            <Check className='h-3 w-3' />
                            Chosen
                          </Badge>
                        )}
                      </div>
                      <p className='text-muted-foreground mt-1 text-xs'>{option.description}</p>
                    </div>
                  </div>
                </td>

                {/* Pros */}
                <td className='p-3 align-top'>
                  <ul className='space-y-1.5'>
                    {option.pros && option.pros.length > 0 ? (
                      option.pros.map((pro, i) => (
                        <li
                          key={i}
                          className='text-muted-foreground flex items-start gap-1.5 text-xs'
                        >
                          <Check className='mt-0.5 h-3 w-3 shrink-0 text-green-500' />
                          <span>{pro}</span>
                        </li>
                      ))
                    ) : (
                      <li className='text-muted-foreground text-xs italic opacity-50'>
                        No pros listed
                      </li>
                    )}
                  </ul>
                </td>

                {/* Cons */}
                <td className='p-3 align-top'>
                  <ul className='space-y-1.5'>
                    {option.cons && option.cons.length > 0 ? (
                      option.cons.map((con, i) => (
                        <li
                          key={i}
                          className='text-muted-foreground flex items-start gap-1.5 text-xs'
                        >
                          <X className='mt-0.5 h-3 w-3 shrink-0 text-red-500' />
                          <span>{con}</span>
                        </li>
                      ))
                    ) : (
                      <li className='text-muted-foreground text-xs italic opacity-50'>
                        No cons listed
                      </li>
                    )}
                  </ul>
                </td>

                {/* Score */}
                {showScoring && (
                  <td className='p-3 text-right align-top'>
                    <div className='flex flex-col items-end gap-1'>
                      <span
                        className={`text-sm font-bold ${
                          calculateScore(option) > 0
                            ? 'text-green-600'
                            : calculateScore(option) < 0
                              ? 'text-red-600'
                              : 'text-muted-foreground'
                        }`}
                      >
                        {calculateScore(option) > 0 ? '+' : ''}
                        {calculateScore(option)}
                      </span>
                      <span className='text-muted-foreground text-xs'>
                        {(option.pros?.length ?? 0) - (option.cons?.length ?? 0)} net
                      </span>
                    </div>
                  </td>
                )}

                {/* Actions */}
                {editable && (
                  <td className='p-3 text-right align-top'>
                    <div className='flex items-center justify-end gap-1'>
                      {onOptionEdit && (
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-6 w-6 p-0'
                          onClick={() => {
                            onOptionEdit(option);
                          }}
                          title='Edit option'
                        >
                          <Edit2 className='h-3 w-3' />
                        </Button>
                      )}
                      {onOptionRemove && (
                        <Button
                          variant='ghost'
                          size='sm'
                          className='h-6 w-6 p-0 text-red-600 hover:bg-red-50 hover:text-red-700'
                          onClick={() => {
                            onOptionRemove(option.id);
                          }}
                          title='Remove option'
                        >
                          <X className='h-3 w-3' />
                        </Button>
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
