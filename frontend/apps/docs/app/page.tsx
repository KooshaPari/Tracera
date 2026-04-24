import Link from 'next/link';

export default function HomePage(): React.JSX.Element {
  return (
    <main className='flex min-h-screen flex-col items-center justify-center p-24'>
      <div className='max-w-5xl w-full items-center justify-between text-center'>
        <h1 className='text-6xl font-bold mb-4'>TracerTM Documentation</h1>
        <p className='text-xl text-muted-foreground mb-8'>
          Complete documentation for the TracerTM platform
        </p>
        <div className='flex gap-4 justify-center'>
          <Link
            href='/docs'
            className='inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2'
          >
            Get Started
          </Link>
          <Link
            href='/api'
            className='inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2'
          >
            API Reference
          </Link>
        </div>
      </div>
    </main>
  );
}
