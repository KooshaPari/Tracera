import { Plus, Trash2, X } from 'lucide-react';
import { useState } from 'react';

import { Badge, Button, Card, cn } from '@tracertm/ui';

export type TableExample = Record<string, string>;

interface ExamplesTableProps {
  data: TableExample[];
  columns: string[];
  onDataChange?: (data: TableExample[]) => void;
  onColumnsChange?: (columns: string[]) => void;
  editable?: boolean;
  className?: string;
  title?: string;
}

export function ExamplesTable({
  data,
  columns,
  onDataChange,
  onColumnsChange,
  editable = true,
  className,
  title = 'Examples',
}: ExamplesTableProps) {
  const [editingCell, setEditingCell] = useState<{
    rowIndex: number;
    colName: string;
  } | null>(null);
  const [editValue, setEditValue] = useState('');

  const handleCellChange = (rowIndex: number, colName: string, value: string) => {
    const newData = [...data];
    newData[rowIndex] ??= {};
    newData[rowIndex][colName] = value;
    onDataChange?.(newData);
  };

  const handleAddRow = () => {
    const newRow: TableExample = {};
    columns.forEach((col) => {
      newRow[col] = '';
    });
    onDataChange?.([...data, newRow]);
  };

  const handleRemoveRow = (rowIndex: number) => {
    const newData = data.filter((_, idx) => idx !== rowIndex);
    onDataChange?.(newData);
  };

  const handleAddColumn = () => {
    const newColName = `Column ${columns.length + 1}`;
    onColumnsChange?.([...columns, newColName]);

    // Add empty values to all rows
    const newData = data.map((row) => ({
      ...row,
      [newColName]: '',
    }));
    onDataChange?.(newData);
  };

  const handleRemoveColumn = (colName: string) => {
    const newColumns = columns.filter((c) => c !== colName);
    onColumnsChange?.(newColumns);

    // Remove column from all rows
    const newData = data.map((row) => {
      const { [colName]: _, ...rest } = row;
      return rest;
    });
    onDataChange?.(newData);
  };

  const handleRenameColumn = (oldName: string, newName: string) => {
    if (!newName.trim() || newName === oldName) {
      return;
    }

    const newColumns = columns.map((c) => (c === oldName ? newName : c));
    onColumnsChange?.(newColumns);

    // Update keys in all rows
    const newData = data.map((row) => {
      const { [oldName]: value, ...rest } = row;
      return {
        ...rest,
        [newName]: value ?? '',
      };
    });
    onDataChange?.(newData);
  };

  return (
    <div className={cn('space-y-3', className)}>
      <div className='flex items-center justify-between'>
        <div className='flex items-center gap-2'>
          <Badge variant='secondary' className='text-xs'>
            <span className='font-semibold'>{data.length}</span>
            <span className='ml-1'>examples</span>
          </Badge>
        </div>
        {title && <h3 className='text-muted-foreground text-sm font-semibold'>{title}</h3>}
      </div>

      <Card className='border-border/50 overflow-hidden border'>
        <div className='overflow-x-auto'>
          <table className='w-full text-sm'>
            {/* Header */}
            <thead className='bg-muted/50 border-border/50 border-b'>
              <tr>
                {editable && (
                  <th className='text-muted-foreground w-10 px-3 py-2 text-center text-xs font-medium'>
                    #
                  </th>
                )}
                {columns.map((col) => (
                  <th
                    key={col}
                    className='text-muted-foreground bg-muted/30 group relative px-3 py-2 text-left font-medium'
                  >
                    <div className='flex min-w-max items-center justify-between gap-2'>
                      <input
                        type='text'
                        value={col}
                        onChange={(e) => {
                          handleRenameColumn(col, e.target.value);
                        }}
                        className={cn(
                          'text-xs font-semibold bg-transparent border-0 outline-none',
                          editable ? 'cursor-text' : 'cursor-default',
                        )}
                        disabled={!editable}
                      />
                      {editable && (
                        <button
                          onClick={() => {
                            handleRemoveColumn(col);
                          }}
                          className='hover:bg-destructive/10 rounded p-1 opacity-0 transition-opacity group-hover:opacity-100'
                          title='Remove column'
                        >
                          <X className='text-destructive h-3 w-3' />
                        </button>
                      )}
                    </div>
                  </th>
                ))}
                {editable && (
                  <th className='w-10 px-3 py-2 text-center'>
                    <button
                      onClick={handleAddColumn}
                      className='hover:bg-muted rounded p-1 transition-colors'
                      title='Add column'
                    >
                      <Plus className='text-muted-foreground h-3 w-3' />
                    </button>
                  </th>
                )}
              </tr>
            </thead>

            {/* Body */}
            <tbody>
              {data.map((row, rowIndex) => (
                <tr
                  key={rowIndex}
                  className='border-border/50 hover:bg-muted/30 border-b transition-colors'
                >
                  {editable && (
                    <td className='text-muted-foreground px-3 py-2 text-center font-mono text-xs'>
                      {rowIndex + 1}
                    </td>
                  )}
                  {columns.map((col) => (
                    <td
                      key={`${rowIndex}-${col}`}
                      className='border-border/25 border-r px-3 py-2 text-xs last:border-r-0'
                    >
                      {editingCell?.rowIndex === rowIndex && editingCell?.colName === col ? (
                        <input
                          type='text'
                          value={editValue}
                          onChange={(e) => {
                            setEditValue(e.target.value);
                          }}
                          onBlur={() => {
                            handleCellChange(rowIndex, col, editValue);
                            setEditingCell(null);
                          }}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleCellChange(rowIndex, col, editValue);
                              setEditingCell(null);
                            } else if (e.key === 'Escape') {
                              setEditingCell(null);
                            }
                          }}
                          className='bg-primary/10 border-primary/30 w-full rounded border px-2 py-1 outline-none'
                        />
                      ) : (
                        <div
                          onClick={() => {
                            if (editable) {
                              setEditingCell({ colName: col, rowIndex });
                              setEditValue(row[col] ?? '');
                            }
                          }}
                          className={cn(
                            'px-2 py-1 rounded',
                            editable ? 'cursor-text hover:bg-muted/50' : '',
                          )}
                        >
                          {row[col] ?? <span className='text-muted-foreground/50'>—</span>}
                        </div>
                      )}
                    </td>
                  ))}
                  {editable && (
                    <td className='px-3 py-2 text-center'>
                      <button
                        onClick={() => {
                          handleRemoveRow(rowIndex);
                        }}
                        className='hover:bg-destructive/10 rounded p-1 transition-colors'
                        title='Remove row'
                      >
                        <Trash2 className='text-destructive h-3 w-3' />
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {editable && data.length === 0 && (
        <div className='text-muted-foreground py-6 text-center text-sm'>
          <p>No examples yet</p>
        </div>
      )}

      {editable && (
        <Button onClick={handleAddRow} variant='outline' size='sm' className='w-full gap-2'>
          <Plus className='h-4 w-4' />
          Add Example
        </Button>
      )}
    </div>
  );
}
