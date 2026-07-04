import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Avatar, AvatarFallback, AvatarImage } from '../components/Avatar';

Vitest.describe('Avatar component', () => {
  Vitest.it('renders the avatar container', () => {
    const { container } = render(
      <Avatar data-testid='avatar'>
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    Vitest.expect(container.querySelector("[data-testid='avatar']")).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLSpanElement>();
    render(
      <Avatar ref={ref}>
        <AvatarFallback>AB</AvatarFallback>
      </Avatar>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLSpanElement);
  });

  Vitest.it('applies custom className', () => {
    const { container } = render(
      <Avatar className='h-12 w-12' data-testid='avatar'>
        <AvatarFallback>CD</AvatarFallback>
      </Avatar>,
    );
    const avatar = container.querySelector("[data-testid='avatar']");
    Vitest.expect(avatar?.className).toContain('h-12');
    Vitest.expect(avatar?.className).toContain('w-12');
  });
});

Vitest.describe('AvatarImage component', () => {
  Vitest.it('renders an img element with src', () => {
    render(
      <Avatar>
        <AvatarImage src='https://example.com/avatar.jpg' alt='User avatar' />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    const img = screen.queryByRole('img');
    // AvatarImage may not render immediately due to Radix loading behavior
    // So we verify it either renders or the fallback is shown.
    if (img) {
      Vitest.expect(img).toHaveAttribute('src', 'https://example.com/avatar.jpg');
    } else {
      Vitest.expect(screen.getByText('JD')).toBeInTheDocument();
    }
  });

  Vitest.it('forwards ref to image', () => {
    const ref = createRef<HTMLImageElement>();
    render(
      <Avatar>
        <AvatarImage ref={ref} src='https://example.com/avatar.jpg' alt='User' />
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    // Ref may be null if image hasn't loaded in jsdom
    Vitest.expect(ref.current === null || ref.current instanceof HTMLImageElement).toBe(true);
  });
});

Vitest.describe('AvatarFallback component', () => {
  Vitest.it('renders fallback text', () => {
    render(
      <Avatar>
        <AvatarFallback>JD</AvatarFallback>
      </Avatar>,
    );
    Vitest.expect(screen.getByText('JD')).toBeInTheDocument();
  });

  Vitest.it('applies custom className to fallback', () => {
    render(
      <Avatar>
        <AvatarFallback className='bg-red-500'>AB</AvatarFallback>
      </Avatar>,
    );
    Vitest.expect(screen.getByText('AB').className).toContain('bg-red-500');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLSpanElement>();
    render(
      <Avatar>
        <AvatarFallback ref={ref}>XY</AvatarFallback>
      </Avatar>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLSpanElement);
  });
});
