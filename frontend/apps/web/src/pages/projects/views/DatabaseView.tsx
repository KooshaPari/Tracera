import { ChevronDown, ChevronRight, Database, Key, Link2, Table2 } from 'lucide-react';
import { useState } from 'react';

interface Column {
  name: string;
  type: string;
  nullable: boolean;
  isPrimary?: boolean;
  isForeign?: boolean;
  references?: string;
}

interface TableDef {
  id: string;
  name: string;
  description: string;
  columns: Column[];
  rowCount: number;
}

const tables: TableDef[] = [
  {
    columns: [
      { isPrimary: true, name: 'id', nullable: false, type: 'UUID' },
      { name: 'name', nullable: false, type: 'VARCHAR(255)' },
      { name: 'description', nullable: true, type: 'TEXT' },
      { name: 'created_at', nullable: false, type: 'TIMESTAMP' },
      { name: 'updated_at', nullable: false, type: 'TIMESTAMP' },
    ],
    description: 'Project containers',
    id: '1',
    name: 'projects',
    rowCount: 12,
  },
  {
    columns: [
      { isPrimary: true, name: 'id', nullable: false, type: 'UUID' },
      {
        isForeign: true,
        name: 'project_id',
        nullable: false,
        references: 'projects.id',
        type: 'UUID',
      },
      { name: 'view', nullable: false, type: 'VARCHAR(50)' },
      { name: 'type', nullable: false, type: 'VARCHAR(50)' },
      { name: 'title', nullable: false, type: 'VARCHAR(500)' },
      { name: 'description', nullable: true, type: 'TEXT' },
      { name: 'status', nullable: false, type: 'VARCHAR(50)' },
      { name: 'priority', nullable: true, type: 'VARCHAR(20)' },
      {
        isForeign: true,
        name: 'parent_id',
        nullable: true,
        references: 'items.id',
        type: 'UUID',
      },
      { name: 'owner', nullable: true, type: 'VARCHAR(255)' },
      { name: 'metadata', nullable: true, type: 'JSONB' },
      { name: 'version', nullable: false, type: 'INTEGER' },
      { name: 'created_at', nullable: false, type: 'TIMESTAMP' },
      { name: 'updated_at', nullable: false, type: 'TIMESTAMP' },
    ],
    description: 'Requirements, code, tests - all item types',
    id: '2',
    name: 'items',
    rowCount: 1847,
  },
  {
    columns: [
      { isPrimary: true, name: 'id', nullable: false, type: 'UUID' },
      {
        isForeign: true,
        name: 'project_id',
        nullable: false,
        references: 'projects.id',
        type: 'UUID',
      },
      {
        isForeign: true,
        name: 'source_id',
        nullable: false,
        references: 'items.id',
        type: 'UUID',
      },
      {
        isForeign: true,
        name: 'target_id',
        nullable: false,
        references: 'items.id',
        type: 'UUID',
      },
      { name: 'type', nullable: false, type: 'VARCHAR(50)' },
      { name: 'description', nullable: true, type: 'TEXT' },
      { name: 'metadata', nullable: true, type: 'JSONB' },
      { name: 'created_at', nullable: false, type: 'TIMESTAMP' },
    ],
    description: 'Traceability relationships between items',
    id: '3',
    name: 'links',
    rowCount: 523,
  },
  {
    columns: [
      { isPrimary: true, name: 'id', nullable: false, type: 'UUID' },
      {
        isForeign: true,
        name: 'item_id',
        nullable: false,
        references: 'items.id',
        type: 'UUID',
      },
      { name: 'version', nullable: false, type: 'INTEGER' },
      { name: 'data', nullable: false, type: 'JSONB' },
      { name: 'changed_by', nullable: true, type: 'VARCHAR(255)' },
      { name: 'created_at', nullable: false, type: 'TIMESTAMP' },
    ],
    description: 'Version history for items',
    id: '4',
    name: 'item_history',
    rowCount: 4521,
  },
];

export function DatabaseView() {
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['2']));

  const toggle = (id: string) => {
    const next = new Set(expanded);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setExpanded(next);
  };

  return (
    <div className='space-y-4'>
      <div className='flex items-center justify-between'>
        <h3 className='text-lg font-semibold'>Database View</h3>
        <div className='text-muted-foreground flex items-center gap-4 text-sm'>
          <span className='flex items-center gap-1'>
            <Database className='h-4 w-4' /> SQLite
          </span>
          <span>{tables.length} tables</span>
          <span>{tables.reduce((acc, t) => acc + t.rowCount, 0).toLocaleString()} total rows</span>
        </div>
      </div>

      <div className='rounded-lg border'>
        {tables.map((table) => (
          <div key={table.id} className='border-b last:border-b-0'>
            <div
              className='hover:bg-accent/50 flex cursor-pointer items-center gap-3 p-4'
              onClick={() => {
                toggle(table.id);
              }}
            >
              {expanded.has(table.id) ? (
                <ChevronDown className='h-4 w-4' />
              ) : (
                <ChevronRight className='h-4 w-4' />
              )}
              <Table2 className='h-5 w-5 text-emerald-500' />
              <code className='font-medium'>{table.name}</code>
              <span className='text-muted-foreground text-sm'>{table.description}</span>
              <span className='text-muted-foreground ml-auto text-xs'>
                {table.rowCount.toLocaleString()} rows
              </span>
            </div>
            {expanded.has(table.id) && (
              <div className='bg-muted/20 border-t'>
                <table className='w-full text-sm'>
                  <thead>
                    <tr className='text-muted-foreground border-b text-left text-xs'>
                      <th className='p-2 pl-12'>Column</th>
                      <th className='p-2'>Type</th>
                      <th className='p-2'>Nullable</th>
                      <th className='p-2'>Constraints</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns.map((col) => (
                      <tr key={col.name} className='border-b last:border-b-0'>
                        <td className='p-2 pl-12 font-mono'>{col.name}</td>
                        <td className='p-2 font-mono text-xs text-blue-600'>{col.type}</td>
                        <td className='p-2'>{col.nullable ? 'YES' : 'NO'}</td>
                        <td className='flex items-center gap-2 p-2'>
                          {col.isPrimary && (
                            <span className='flex items-center gap-1 text-xs text-yellow-600'>
                              <Key className='h-3 w-3' /> PK
                            </span>
                          )}
                          {col.isForeign && (
                            <span className='flex items-center gap-1 text-xs text-purple-600'>
                              <Link2 className='h-3 w-3' /> → {col.references}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
