import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../components/Accordion';

Vitest.describe('Accordion component', () => {
  const renderAccordion = () =>
    render(
      <Accordion type='single' collapsible>
        <AccordionItem value='item-1'>
          <AccordionTrigger>Section 1</AccordionTrigger>
          <AccordionContent>Content 1</AccordionContent>
        </AccordionItem>
        <AccordionItem value='item-2'>
          <AccordionTrigger>Section 2</AccordionTrigger>
          <AccordionContent>Content 2</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );

  Vitest.it('renders accordion triggers', () => {
    renderAccordion();
    Vitest.expect(screen.getByText('Section 1')).toBeInTheDocument();
    Vitest.expect(screen.getByText('Section 2')).toBeInTheDocument();
  });

  Vitest.it('hides content by default (data-state=closed)', () => {
    renderAccordion();
    const trigger = screen.getByText('Section 1').closest('button');
    Vitest.expect(trigger).toHaveAttribute('data-state', 'closed');
  });

  Vitest.it('shows content when trigger is clicked', () => {
    renderAccordion();
    fireEvent.click(screen.getByText('Section 1'));
    Vitest.expect(screen.getByText('Content 1')).toBeVisible();
  });

  Vitest.it('updates trigger data-state to open when clicked', () => {
    renderAccordion();
    fireEvent.click(screen.getByText('Section 1'));
    const trigger = screen.getByText('Section 1').closest('button');
    Vitest.expect(trigger).toHaveAttribute('data-state', 'open');
  });

  Vitest.it('supports default open value', () => {
    render(
      <Accordion type='single' defaultValue='item-1'>
        <AccordionItem value='item-1'>
          <AccordionTrigger>Section 1</AccordionTrigger>
          <AccordionContent>Open by default</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    Vitest.expect(screen.getByText('Open by default')).toBeVisible();
  });
});

Vitest.describe('AccordionItem component', () => {
  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <Accordion type='single' collapsible>
        <AccordionItem ref={ref} value='item-1'>
          <AccordionTrigger>Trigger</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(
      <Accordion type='single' collapsible>
        <AccordionItem className='custom-item' value='item-1' data-testid='accordion-item'>
          <AccordionTrigger>Trigger</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    Vitest.expect(screen.getByTestId('accordion-item').className).toContain('custom-item');
  });
});

Vitest.describe('AccordionTrigger component', () => {
  Vitest.it('renders as a button', () => {
    render(
      <Accordion type='single' collapsible>
        <AccordionItem value='item-1'>
          <AccordionTrigger>Click me</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    Vitest.expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });
});
