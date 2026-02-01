import { memo } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { AlertCircle, RefreshCw, Copy, Bug } from 'lucide-react';

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
  const errorDetails: ErrorDetails = typeof error === 'string'
    ? { message: error }
    : error instanceof Error
    ? {
        message: error.message,
        ...(error.stack !== undefined && { stack: error.stack }),
      }
    : error;

  const handleCopyError = () => {
    const errorText = `Error: ${errorDetails.message}\n${errorDetails.stack || ''}`;
    navigator.clipboard.writeText(errorText);
  };

  if (variant === 'inline') {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription className="flex items-center justify-between">
          <span>{errorDetails.message}</span>
          {onRetry && (
            <Button size="sm" variant="outline" onClick={onRetry}>
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className="border-destructive">
      <CardHeader>
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-destructive">
              Unable to load graph
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              {errorDetails.message}
            </p>
          </div>
        </div>
      </CardHeader>

      {showDetails && errorDetails.stack && (
        <CardContent>
          <Accordion type="single" collapsible>
            <AccordionItem value="details" className="border-0">
              <AccordionTrigger className="text-xs text-muted-foreground">
                Show technical details
              </AccordionTrigger>
              <AccordionContent>
                <pre className="text-xs bg-muted p-3 rounded overflow-auto max-h-48">
                  {errorDetails.stack}
                </pre>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      )}

      <CardFooter className="flex gap-2">
        {onRetry && (
          <Button size="sm" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-2" />
            Retry
          </Button>
        )}
        <Button size="sm" variant="outline" onClick={handleCopyError}>
          <Copy className="h-3 w-3 mr-2" />
          Copy error
        </Button>
        {onReportBug && (
          <Button size="sm" variant="outline" onClick={() => onReportBug(errorDetails)}>
            <Bug className="h-3 w-3 mr-2" />
            Report bug
          </Button>
        )}
      </CardFooter>
    </Card>
  );
});
