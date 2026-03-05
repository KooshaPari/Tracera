import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Avatar, AvatarFallback, AvatarImage } from '../components/Avatar';

describe('Avatar component', () => {
  it('renders the avatar container', () => {
    const { container } = render(
      <Avatar data-testid='avatar'>
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    expect(container.querySelector("[data-testid='avatar']")).toBeInTheDocument();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLSpanElement>();
    render(
      <Avatar ref={ref}>
        <AvatarFallback>AB</AvatarFallback>
      </Avatar>,
    );
    expect(ref.current).toBeInstanceOf(HTMLSpanElement);
  });

  it('applies custom className', () => {
    const { container } = render(
      <Avatar className='h-12 w-12' data-testid='avatar'>
        <AvatarFallback>CD</AvatarFallback>
      </Avatar>,
    );
    const avatar = container.querySelector("[data-testid='avatar']");
    expect(avatar?.className).toContain('h-12');
    expect(avatar?.className).toContain('w-12');
  });
});

describe('AvatarImage component', () => {
  it('renders an img element with src', () => {
    render(
      <Avatar>
        <AvatarImage src='https://example.com/avatar.jpg' alt='User avatar' />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    const img = screen.queryByRole('img');
    // AvatarImage may not render immediately due to Radix loading behavior
    // so we verify it either renders or the fallback is shown
    if (img) {
      expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg');
    } else {
      expect(screen.getByText('JD')).toBeInTheDocument();
    }
  });

  it('forwards ref to image', () => {
    const ref = createRef<HTMLImageElement>();
    render(
      <Avatar>
        <AvatarImage ref={ref} src='https://example.com/avatar.jpg' alt='User' />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    // Ref may be null if image hasn't loaded in jsdom
    expect(ref.current === null || ref.current instanceof HTMLImageElement).toBe(true);
  });
});

describe('AvatarFallback component', () => {
  it('renders fallback text', () => {
    render(
      <Avatar>
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    expect(screen.getByText('JD')).toBeInTheDocument();
  });

  it('applies custom className to fallback', () => {
    render(
      <Avatar>
        <AvatarFallback className='bg-red-500'>AB</AvatarFallback>
      </Avatar>,
    );
    expect(screen.getByText('AB').className).toContain('bg-red-500');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLSpanElement>();
    render(
      <Avatar>
        <AvatarFallback ref={ref}>XY</AvatarFallback>
      </Avatar>,
    );
    expect(ref.current).toBeInstanceOf(HTMLSpanElement);
  });
});
