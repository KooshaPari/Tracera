'use client';

/**
 * Optimized Image Component
 *
 * Wraps Next.js Image with best practices for performance:
 * - AVIF/WebP formats
 * - Lazy loading
 * - Blur placeholders
 * - Responsive sizing
 */

import Image from 'next/image';
import { useState } from 'react';

import { cn } from '@/lib/utils';

type OptimizedImageProps =
  | {
      src: string;
      alt: string;
      fill: true;
      className?: string;
      priority?: boolean;
      quality?: number;
      sizes?: string;
      objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
      blurDataURL?: string;
      width?: never;
      height?: never;
    }
  | {
      src: string;
      alt: string;
      fill?: false;
      width: number;
      height: number;
      className?: string;
      priority?: boolean;
      quality?: number;
      sizes?: string;
      objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
      blurDataURL?: string;
    };

/**
 * Optimized image component with automatic format selection and lazy loading
 *
 * Features:
 * - Automatic AVIF/WebP conversion
 * - Lazy loading by default (disable with priority prop)
 * - Blur placeholder during load
 * - Responsive image sizing
 * - Loading state indicator
 *
 * @example
 * // Responsive image
 * <OptimizedImage
 *   src="/images/hero.jpg"
 *   alt="Hero image"
 *   width={1200}
 *   height={600}
 *   sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
 * />
 *
 * @example
 * // Fill container
 * <OptimizedImage
 *   src="/images/background.jpg"
 *   alt="Background"
 *   fill
 *   objectFit="cover"
 *   priority
 * />
 */
export function OptimizedImage({
  src,
  alt,
  width,
  height,
  fill = false,
  className = '',
  priority = false,
  quality = 85,
  sizes,
  objectFit = 'cover',
  blurDataURL,
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const isFill = fill === true;
  const loadingProps = priority ? {} : { loading: 'lazy' as const };
  const placeholder = blurDataURL ? ('blur' as const) : ('empty' as const);
  const blurProps = blurDataURL ? { blurDataURL } : {};
  const resolvedSizes =
    sizes || (isFill ? '100vw' : '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw');
  const imageClassName = cn(
    'duration-300 ease-in-out',
    isLoading ? 'scale-105 blur-sm' : 'scale-100 blur-0',
    isFill && `object-${objectFit}`,
  );

  return (
    <div className={cn('relative overflow-hidden', fill && 'w-full h-full', className)}>
      {isFill ? (
        <Image
          src={src}
          alt={alt}
          fill
          quality={quality}
          sizes={resolvedSizes}
          priority={priority}
          {...loadingProps}
          placeholder={placeholder}
          {...blurProps}
          className={imageClassName}
          onLoad={() => setIsLoading(false)}
        />
      ) : (
        <Image
          src={src}
          alt={alt}
          width={width!}
          height={height!}
          quality={quality}
          sizes={resolvedSizes}
          priority={priority}
          {...loadingProps}
          placeholder={placeholder}
          {...blurProps}
          className={imageClassName}
          onLoad={() => setIsLoading(false)}
        />
      )}
      {isLoading && <div className='absolute inset-0 bg-muted animate-pulse' aria-hidden='true' />}
    </div>
  );
}

/**
 * Documentation Image Component
 *
 * Specialized for documentation images with preset responsive sizes
 */
export function DocImage({
  src,
  alt,
  caption,
  priority = false,
}: {
  src: string;
  alt: string;
  caption?: string;
  priority?: boolean;
}) {
  return (
    <figure className='my-8'>
      <OptimizedImage
        src={src}
        alt={alt}
        width={1200}
        height={675}
        priority={priority}
        sizes='(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px'
        className='rounded-lg border shadow-sm'
      />
      {caption && (
        <figcaption className='mt-2 text-center text-sm text-muted-foreground'>
          {caption}
        </figcaption>
      )}
    </figure>
  );
}

/**
 * Avatar Image Component
 *
 * Optimized for small circular profile images
 */
export function Avatar({ src, alt, size = 40 }: { src: string; alt: string; size?: number }) {
  return (
    <div
      className='relative rounded-full overflow-hidden bg-muted'
      style={{ height: size, width: size }}
    >
      <OptimizedImage
        src={src}
        alt={alt}
        width={size}
        height={size}
        objectFit='cover'
        sizes={`${size}px`}
      />
    </div>
  );
}

/**
 * Logo Image Component
 *
 * Optimized for logo images with high priority loading
 */
export function Logo({
  src,
  alt,
  width = 120,
  height = 40,
}: {
  src: string;
  alt: string;
  width?: number;
  height?: number;
}) {
  return (
    <OptimizedImage
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority
      quality={100}
      sizes={`${width}px`}
      objectFit='contain'
    />
  );
}
