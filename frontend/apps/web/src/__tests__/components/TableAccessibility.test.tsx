/**
 * Base Table Component Accessibility Tests
 * Tests the accessible table components directly
 */

import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../components/ui/table';

describe('Table Components - Accessibility', () => {
  describe('Base Table Component', () => {
    it('should render table with role and aria-label', () => {
      const { container } = render(
        <Table ariaLabel='Test table'>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveAttribute('role', 'table');
      expect(table).toHaveAttribute('aria-label', 'Test table');
    });

    it('should support aria-labelledby', () => {
      const { container } = render(
        <Table ariaLabelledBy='table-title'>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveAttribute('aria-labelledby', 'table-title');
    });

    it('should support aria-describedby', () => {
      const { container } = render(
        <Table ariaDescribedBy='table-instructions'>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveAttribute('aria-describedby', 'table-instructions');
    });
  });

  describe('TableHeader Component', () => {
    it('should have rowgroup role', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const thead = container.querySelector('thead');
      expect(thead).toHaveAttribute('role', 'rowgroup');
    });
  });

  describe('TableBody Component', () => {
    it('should have rowgroup role', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const tbody = container.querySelector('tbody');
      expect(tbody).toHaveAttribute('role', 'rowgroup');
    });
  });

  describe('TableRow Component', () => {
    it('should have row role', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const tr = container.querySelector('tr');
      expect(tr).toHaveAttribute('role', 'row');
    });

    it('should support aria-rowindex', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow rowIndex={1}>
              <TableCell>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const tr = container.querySelector('tr');
      expect(tr).toHaveAttribute('aria-rowindex', '1');
    });

    it('should support aria-selected', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow isSelected>
              <TableCell>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const tr = container.querySelector('tr');
      expect(tr).toHaveAttribute('aria-selected', 'true');
    });
  });

  describe('TableHead Component', () => {
    it('should have columnheader role', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const th = container.querySelector('th');
      expect(th).toHaveAttribute('role', 'columnheader');
    });

    it('should support aria-colindex', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead colIndex={1}>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const th = container.querySelector('th');
      expect(th).toHaveAttribute('aria-colindex', '1');
    });

    it('should support aria-sort', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead sortDirection='ascending'>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const th = container.querySelector('th');
      expect(th).toHaveAttribute('aria-sort', 'ascending');
    });

    it('should have cursor-pointer when sortable', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead isSortable>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const th = container.querySelector('th');
      expect(th).toHaveClass('cursor-pointer');
    });

    it('should default to aria-sort none when not sorted', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const th = container.querySelector('th');
      expect(th).toHaveAttribute('aria-sort', 'none');
    });
  });

  describe('TableCell Component', () => {
    it('should have gridcell role', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const td = container.querySelector('td');
      expect(td).toHaveAttribute('role', 'gridcell');
    });

    it('should support aria-colindex', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell colIndex={1}>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const td = container.querySelector('td');
      expect(td).toHaveAttribute('aria-colindex', '1');
    });

    it('should support aria-label', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell ariaLabel='Cell label'>Cell</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const td = container.querySelector('td');
      expect(td).toHaveAttribute('aria-label', 'Cell label');
    });

    it('should generate aria-label from headerText and content', () => {
      const { container } = render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell headerText='Name'>John</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const td = container.querySelector('td');
      expect(td).toHaveAttribute('aria-label');
      const label = td?.getAttribute('aria-label');
      expect(label).toContain('Name');
      expect(label).toContain('John');
    });
  });

  describe('Complete Table Structure', () => {
    it('should render complete accessible table', () => {
      const { container } = render(
        <Table ariaLabel='Sample data table'>
          <TableHeader>
            <TableRow>
              <TableHead colIndex={1} isSortable sortDirection='ascending'>
                Name
              </TableHead>
              <TableHead colIndex={2}>Email</TableHead>
              <TableHead colIndex={3}>Role</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow rowIndex={2}>
              <TableCell colIndex={1} headerText='Name'>
                John Doe
              </TableCell>
              <TableCell colIndex={2} headerText='Email'>
                john@example.com
              </TableCell>
              <TableCell colIndex={3} headerText='Role'>
                Admin
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveAttribute('role', 'table');
      expect(table).toHaveAttribute('aria-label');

      const thead = container.querySelector('thead');
      expect(thead).toHaveAttribute('role', 'rowgroup');

      const tbody = container.querySelector('tbody');
      expect(tbody).toHaveAttribute('role', 'rowgroup');

      const headers = container.querySelectorAll('th');
      expect(headers.length).toBe(3);
      headers.forEach((header, index) => {
        expect(header).toHaveAttribute('role', 'columnheader');
        expect(header).toHaveAttribute('aria-colindex', String(index + 1));
      });

      const cells = container.querySelectorAll('td');
      expect(cells.length).toBe(3);
      cells.forEach((cell, index) => {
        expect(cell).toHaveAttribute('role', 'gridcell');
        expect(cell).toHaveAttribute('aria-colindex', String(index + 1));
      });
    });

    it('should support multiple rows with proper indices', () => {
      const { container } = render(
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead colIndex={1}>Name</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow rowIndex={2}>
              <TableCell colIndex={1}>Row 1</TableCell>
            </TableRow>
            <TableRow rowIndex={3}>
              <TableCell colIndex={1}>Row 2</TableCell>
            </TableRow>
            <TableRow rowIndex={4}>
              <TableCell colIndex={1}>Row 3</TableCell>
            </TableRow>
          </TableBody>
        </Table>,
      );

      const rows = container.querySelectorAll('tr');
      expect(rows.length).toBe(4); // Header + 3 rows

      // Data rows should have aria-rowindex
      expect(rows[1]).toHaveAttribute('aria-rowindex', '2');
      expect(rows[2]).toHaveAttribute('aria-rowindex', '3');
      expect(rows[3]).toHaveAttribute('aria-rowindex', '4');
    });
  });

  describe('Accessibility Best Practices', () => {
    it('should support both aria-label and aria-labelledby', () => {
      const { container } = render(
        <Table ariaLabelledBy='title-id' ariaDescribedBy='desc-id'>
          <TableHeader>
            <TableRow>
              <TableHead>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveAttribute('aria-labelledby', 'title-id');
      expect(table).toHaveAttribute('aria-describedby', 'desc-id');
    });

    it('should allow custom className alongside accessibility props', () => {
      const { container } = render(
        <Table ariaLabel='Test table' className='custom-table-class'>
          <TableHeader>
            <TableRow>
              <TableHead className='custom-header'>Header</TableHead>
            </TableRow>
          </TableHeader>
        </Table>,
      );

      const table = container.querySelector('table');
      expect(table).toHaveClass('custom-table-class');

      const th = container.querySelector('th');
      expect(th).toHaveClass('custom-header');
    });
  });
});
