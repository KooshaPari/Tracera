export function Settings() {
  return (
    <div className='space-y-6'>
      <h2 className='text-2xl font-bold'>Settings</h2>
      <div className='max-w-2xl space-y-6'>
        <div className='rounded-lg border p-6'>
          <h3 className='font-semibold'>General</h3>
          <div className='mt-4 space-y-4'>
            <div>
              <label className='text-sm font-medium'>Theme</label>
              <select className='mt-1 h-10 w-full rounded-lg border px-3'>
                <option>System</option>
                <option>Light</option>
                <option>Dark</option>
              </select>
            </div>
          </div>
        </div>
        <div className='rounded-lg border p-6'>
          <h3 className='font-semibold'>API Configuration</h3>
          <div className='mt-4'>
            <label className='text-sm font-medium'>Backend URL</label>
            <input
              type='text'
              defaultValue='http://localhost:4000'
              className='mt-1 h-10 w-full rounded-lg border px-3'
            />
          </div>
        </div>
      </div>
    </div>
  );
}
