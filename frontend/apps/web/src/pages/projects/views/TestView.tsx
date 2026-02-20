import { CheckCircle, Clock, XCircle } from 'lucide-react';

const suites = [
  { failed: 2, id: '1', name: 'Unit Tests', passed: 45, pending: 3 },
  { failed: 0, id: '2', name: 'Integration Tests', passed: 12, pending: 1 },
  { failed: 1, id: '3', name: 'E2E Tests', passed: 8, pending: 0 },
];

export function TestView() {
  return (
    <div className='space-y-4'>
      <h3 className='text-lg font-semibold'>Test View</h3>
      <div className='grid gap-4 md:grid-cols-3'>
        {suites.map((suite) => (
          <div key={suite.id} className='rounded-lg border p-4'>
            <h4 className='font-medium'>{suite.name}</h4>
            <div className='mt-4 space-y-2'>
              <div className='flex items-center gap-2'>
                <CheckCircle className='h-4 w-4 text-green-500' />
                <span className='text-sm'>{suite.passed} passed</span>
              </div>
              <div className='flex items-center gap-2'>
                <XCircle className='h-4 w-4 text-red-500' />
                <span className='text-sm'>{suite.failed} failed</span>
              </div>
              <div className='flex items-center gap-2'>
                <Clock className='h-4 w-4 text-yellow-500' />
                <span className='text-sm'>{suite.pending} pending</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
