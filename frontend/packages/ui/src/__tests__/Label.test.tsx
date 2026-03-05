import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Label } from '../components/Label';

describe('Label component', () => {
  it('renders as a label element', () => {
    render(<Label>Username</Label>);
    const label = screen.getByText('Username');
    expect(label.tagName).toBe('LABEL');
  });

  it('renders children text', () => {
    render(<Label>Email address</Label>);
    expect(screen.getByText('Email address')).toBeInTheDocument();
  });

  it('associates with input via htmlFor', () => {
    render(
      <>
        <Label htmlFor='email'>Email</Label>
        <input id='email' type='email' />
      </>,
    );
    const label = screen.getByText('Email');
    expect(label).toHaveAttribute('for', 'email');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLLabelElement>();
    render(<Label ref={ref}>Ref test</Label>);
    expect(ref.current).toBeInstanceOf(HTMLLabelElement);
  });

  it('applies custom className', () => {
    render(<Label className='custom-label'>Custom</Label>);
    expect(screen.getByText('Custom').className).toContain('custom-label');
  });

  it('passes through additional HTML attributes', () => {
    render(<Label data-testid='my-label'>Test</Label>);
    expect(screen.getByTestId('my-label')).toBeInTheDocument();
  });
});
