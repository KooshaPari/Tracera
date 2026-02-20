import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '../components/Accordion';

describe('Accordion', () => {
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

  it('renders accordion triggers', () => {
    renderAccordion();
    expect(screen.getByText('Section 1')).toBeInTheDocument();
    expect(screen.getByText('Section 2')).toBeInTheDocument();
  });

  it('hides content by default (data-state=closed)', () => {
    renderAccordion();
    const trigger = screen.getByText('Section 1').closest('button');
    expect(trigger).toHaveAttribute('data-state', 'closed');
  });

  it('shows content when trigger is clicked', () => {
    renderAccordion();
    fireEvent.click(screen.getByText('Section 1'));
    expect(screen.getByText('Content 1')).toBeVisible();
  });

  it('updates trigger data-state to open when clicked', () => {
    renderAccordion();
    fireEvent.click(screen.getByText('Section 1'));
    const trigger = screen.getByText('Section 1').closest('button');
    expect(trigger).toHaveAttribute('data-state', 'open');
  });

  it('supports default open value', () => {
    render(
      <Accordion type='single' defaultValue='item-1'>
        <AccordionItem value='item-1'>
          <AccordionTrigger>Section 1</AccordionTrigger>
          <AccordionContent>Open by default</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    expect(screen.getByText('Open by default')).toBeVisible();
  });
});

describe('AccordionItem', () => {
  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <Accordion type='single' collapsible>
        <AccordionItem ref={ref} value='item-1'>
          <AccordionTrigger>Trigger</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    render(
      <Accordion type='single' collapsible>
        <AccordionItem className='custom-item' value='item-1' data-testid='accordion-item'>
          <AccordionTrigger>Trigger</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    expect(screen.getByTestId('accordion-item').className).toContain('custom-item');
  });
});

describe('AccordionTrigger', () => {
  it('renders as a button', () => {
    render(
      <Accordion type='single' collapsible>
        <AccordionItem value='item-1'>
          <AccordionTrigger>Click me</AccordionTrigger>
          <AccordionContent>Content</AccordionContent>
        </AccordionItem>
      </Accordion>,
    );
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });
});
