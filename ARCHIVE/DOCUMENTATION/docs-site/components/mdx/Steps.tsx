import { ReactNode, Children, isValidElement } from 'react';
import { cn } from '@/lib/utils';

interface StepsProps {
  /** Step children */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Steps - Numbered step-by-step instructions
 *
 * Usage in MDX:
 * ```mdx
 * <Steps>
 *   <Step>
 *     Install the package
 *     ```bash
 *     npm install tracertm
 *     ```
 *   </Step>
 *   <Step>
 *     Configure your environment
 *   </Step>
 *   <Step>
 *     Start using TraceRTM
 *   </Step>
 * </Steps>
 * ```
 */
export function Steps({ children, className }: StepsProps) {
  const childArray = Children.toArray(children).filter(isValidElement);
  const stepCount = childArray.length;

  return (
    <div
      className={cn('my-6', className)}
      role="list"
      aria-label="Step-by-step instructions"
    >
      {Children.map(children, (child, index) => {
        if (!isValidElement(child)) return null;

        return (
          <div
            key={index}
            className="flex gap-4 pb-8 last:pb-0"
            role="listitem"
          >
            {/* Step Number with Connector Line */}
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  'flex items-center justify-center',
                  'w-8 h-8 rounded-full',
                  'bg-primary text-primary-foreground',
                  'text-sm font-semibold flex-shrink-0'
                )}
                aria-label={`Step ${index + 1}`}
              >
                {index + 1}
              </div>
              {/* Connector Line */}
              {index < stepCount - 1 && (
                <div className="w-px flex-1 bg-border mt-2" aria-hidden="true" />
              )}
            </div>

            {/* Step Content */}
            <div className="flex-1 pt-1 min-w-0">
              {(child.props as { children?: ReactNode }).children}
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface StepProps {
  /** Optional step title */
  title?: string;
  /** Step content */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Step - Individual step content
 */
export function Step({ title, children, className }: StepProps) {
  return (
    <div className={cn('', className)}>
      {title && (
        <h4 className="font-semibold text-lg mb-2">{title}</h4>
      )}
      <div
        className={cn(
          'prose prose-sm max-w-none dark:prose-invert',
          '[&>p:first-child]:mt-0',
          '[&>p:last-child]:mb-0',
          '[&>pre]:my-3'
        )}
      >
        {children}
      </div>
    </div>
  );
}

/**
 * StepsCompact - More compact version of steps
 */
export function StepsCompact({ children, className }: StepsProps) {
  return (
    <ol
      className={cn(
        'my-6 space-y-3 list-none pl-0',
        '[counter-reset:step]',
        className
      )}
    >
      {Children.map(children, (child, index) => {
        if (!isValidElement(child)) return null;

        return (
          <li
            key={index}
            className={cn(
              'relative pl-10',
              'before:absolute before:left-0 before:top-0',
              'before:flex before:items-center before:justify-center',
              'before:w-7 before:h-7 before:rounded-full',
              'before:bg-muted before:text-foreground',
              'before:text-sm before:font-medium',
              'before:content-[counter(step)]',
              '[counter-increment:step]'
            )}
          >
            <div className="prose prose-sm max-w-none dark:prose-invert [&>p]:m-0">
              {(child.props as { children?: ReactNode }).children}
            </div>
          </li>
        );
      })}
    </ol>
  );
}

/**
 * StepCompact - Individual compact step
 */
export function StepCompact({ children, className }: Omit<StepProps, 'title'>) {
  return <div className={className}>{children}</div>;
}

/**
 * Checklist - Steps as a checklist (useful for prerequisites)
 */
interface ChecklistProps {
  /** Checklist items */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export function Checklist({ children, className }: ChecklistProps) {
  return (
    <ul className={cn('my-6 space-y-2 list-none pl-0', className)}>
      {Children.map(children, (child, index) => {
        if (!isValidElement(child)) return null;

        return (
          <li key={index} className="flex items-start gap-3">
            <div className="flex items-center justify-center w-5 h-5 mt-0.5 rounded border-2 border-muted-foreground/30 flex-shrink-0">
              {/* Unchecked state - can be made interactive if needed */}
            </div>
            <div className="prose prose-sm max-w-none dark:prose-invert [&>p]:m-0">
              {(child.props as { children?: ReactNode }).children}
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export function ChecklistItem({ children }: { children: ReactNode }) {
  return <div>{children}</div>;
}

export default Steps;
