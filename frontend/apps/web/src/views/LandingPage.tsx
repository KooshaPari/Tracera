import { Link } from '@tanstack/react-router';
import { ArrowRight, GitBranch, Layers, Zap } from 'lucide-react';

import { Button } from '@/components/ui/enterprise-button';

export function LandingPage() {
  return (
    <div className='bg-background text-foreground flex min-h-screen flex-col'>
      {/* Header / Nav */}
      <header className='border-border/40 bg-background/80 fixed top-0 z-50 w-full border-b px-6 py-4 backdrop-blur-sm'>
        <div className='container mx-auto flex items-center justify-between'>
          <div className='flex items-center gap-2 text-xl font-bold'>
            <div className='bg-primary text-primary-foreground flex h-8 w-8 items-center justify-center rounded-lg'>
              T
            </div>
            TraceRTM
          </div>
          <div className='flex items-center gap-4'>
            <Link
              to='/auth/login'
              className='hover:text-primary text-sm font-medium transition-all duration-200 ease-out active:scale-95'
            >
              Login
            </Link>
            <Link to='/auth/register'>
              <Button size='sm' variant='enterprise'>
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className='animate-in-fade-up flex-1 pt-24'>
        {/* Hero Section */}
        <section className='relative overflow-hidden px-6 py-20'>
          {/* Background effects */}
          <div className='bg-primary/5 pointer-events-none absolute top-0 left-1/2 h-[500px] w-full -translate-x-1/2 rounded-full blur-[120px]' />

          <div className='relative z-10 container mx-auto max-w-4xl text-center'>
            <div className='bg-primary/10 text-primary border-primary/20 mb-8 inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium'>
              <span className='relative flex h-2 w-2'>
                <span className='bg-primary absolute inline-flex h-full w-full animate-ping rounded-full opacity-75' />
                <span className='bg-primary relative inline-flex h-2 w-2 rounded-full' />
              </span>
              v2.0 Now Available
            </div>
            <h1 className='from-foreground to-foreground/70 mb-6 bg-gradient-to-r bg-clip-text text-5xl font-bold tracking-tight text-transparent md:text-7xl'>
              Requirements Traceability <br />
              <span className='text-primary'>Reimagined</span>
            </h1>
            <p className='text-muted-foreground mx-auto mb-10 max-w-2xl text-xl leading-relaxed'>
              End-to-end traceability from requirements to code. Visualize dependencies, ensure
              compliance, and ship with confidence.
            </p>
            <div className='flex flex-col items-center justify-center gap-4 sm:flex-row'>
              <Link to='/auth/register'>
                <Button
                  size='lg'
                  variant='enterprise'
                  className='shadow-primary/20 h-12 min-w-[160px] text-base shadow-lg'
                >
                  Start Free Trial
                  <ArrowRight className='ml-2 h-4 w-4' />
                </Button>
              </Link>
              <Link to='/auth/login'>
                <Button size='lg' variant='outline' className='h-12 min-w-[160px] text-base'>
                  View Demo
                </Button>
              </Link>
            </div>

            <div className='border-border/50 bg-card/50 relative mt-20 overflow-hidden rounded-xl border shadow-2xl backdrop-blur-sm'>
              <div className='from-primary/5 pointer-events-none absolute inset-0 bg-gradient-to-tr to-transparent' />
              {/* Placeholder for App Screenshot */}
              <div className='text-muted-foreground bg-muted/20 flex aspect-[16/9] items-center justify-center'>
                <div className='p-8 text-center'>
                  <Layers className='mx-auto mb-4 h-16 w-16 opacity-50' />
                  <p>Interactive Graph View Placeholder</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className='bg-muted/30 px-6 py-24'>
          <div className='container mx-auto max-w-6xl'>
            <div className='mb-16 text-center'>
              <h2 className='mb-4 text-3xl font-bold'>Why TraceRTM?</h2>
              <p className='text-muted-foreground mx-auto max-w-2xl'>
                Built for complex engineering teams who need total visibility and control.
              </p>
            </div>

            <div className='grid gap-8 md:grid-cols-3'>
              <FeatureCard
                icon={<Layers className='h-6 w-6 text-blue-500' />}
                title='Multi-View Visualization'
                description='Switch instantly between Traceability Matrix, Dependency Graph, Kanban Board, and Tree Views.'
              />
              <FeatureCard
                icon={<Zap className='h-6 w-6 text-amber-500' />}
                title='AI-Powered Insights'
                description='Automatically detect missing requirements, compliance gaps, and contradictory specifications.'
              />
              <FeatureCard
                icon={<GitBranch className='h-6 w-6 text-green-500' />}
                title='Code Integration'
                description='Link requirements directly to PRs and commits. Keep documentation in sync with development.'
              />
            </div>
          </div>
        </section>
      </main>

      <footer className='border-border/40 bg-background border-t px-6 py-8'>
        <div className='container mx-auto flex flex-col items-center justify-between gap-4 md:flex-row'>
          <p className='text-muted-foreground text-sm'>© 2026 TraceRTM. All rights reserved.</p>
          <div className='text-muted-foreground flex gap-6 text-sm'>
            <Link to='#' className='hover:text-foreground'>
              Privacy
            </Link>
            <Link to='#' className='hover:text-foreground'>
              Terms
            </Link>
            <Link to='#' className='hover:text-foreground'>
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className='bg-card border-border/50 rounded-2xl border p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-md'>
      <div className='bg-background border-border mb-4 flex h-12 w-12 items-center justify-center rounded-lg border'>
        {icon}
      </div>
      <h3 className='mb-2 text-xl font-bold'>{title}</h3>
      <p className='text-muted-foreground leading-relaxed'>{description}</p>
    </div>
  );
}
