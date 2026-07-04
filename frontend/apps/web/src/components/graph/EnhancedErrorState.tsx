import { AlertCircle, Bug, Copy, RefreshCw } from 'lucide-react';
import { memo } from 'react';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';

interface ErrorDetails {
  message: string;
  stack?: string;
  code?: string;
  timestamp?: Date;
}

interface EnhancedErrorStateProps {
  error: ErrorDetails | Error | string;
  onRetry?: () => void;
  onReportBug?: (error: ErrorDetails) => void;
  showDetails?: boolean;
  variant?: 'inline' | 'card';
}

export const EnhancedErrorState = memo(function EnhancedErrorState({
  error,
  onRetry,
  onReportBug,
  showDetails = true,
  variant = 'card',
}: EnhancedErrorStateProps) {
  const errorDetails: ErrorDetails =
    typeof error === 'string'
      ? { message: error }
      : error instanceof Error
        ? {
            message: error.message,
            ...(error.stack !== undefined && { stack: error.stack }),
          }
        : error;

  const handleCopyError = () => {};

  if (variant === 'inline') {
    return (
      <Alert variant='destructive'>
        <AlertCircle className='h-4 w-4' />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription className='flex items-center justify-between'>
          <span>{errorDetails.message}</span>
          {onRetry && (
            <Button size='sm' variant='outline' onClick={onRetry}>
              <RefreshCw className='mr-1 h-3 w-3' />
              Retry
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className='border-destructive'>
      <CardHeader>
        <div className='flex items-start gap-3'>
          <AlertCircle className='text-destructive mt-0.5 h-5 w-5' />
          <div className='flex-1'>
            <h3 className='text-destructive font-semibold'>Unable to load graph</h3>
            <p className='text-muted-foreground mt-1 text-sm'>{errorDetails.message}</p>
          </div>
        </div>
      </CardHeader>

      {showDetails && errorDetails.stack && (
        <CardContent>
          <Accordion type='single' collapsible>
            <AccordionItem value='details' className='border-0'>
              <AccordionTrigger className='text-muted-foreground text-xs'>
                Show technical details
              </AccordionTrigger>
              <AccordionContent>
                <pre className='bg-muted max-h-48 overflow-auto rounded p-3 text-xs'>
                  {errorDetails.stack}
                </pre>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      )}

      <CardFooter className='flex gap-2'>
        {onRetry && (
          <Button size='sm' onClick={onRetry}>
            <RefreshCw className='mr-2 h-3 w-3' />
            Retry
          </Button>
        )}
        <Button size='sm' variant='outline' onClick={handleCopyError}>
          <Copy className='mr-2 h-3 w-3' />
          Copy error
        </Button>
        {onReportBug && (
          <Button
            size='sm'
            variant='outline'
            onClick={() => {
              onReportBug(errorDetails);
            }}
          >
            <Bug className='mr-2 h-3 w-3' />
            Report bug
          </Button>
        )}
      </CardFooter>
    </Card>
  );
});
