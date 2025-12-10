export default function TestSlugPage({ params }: { params: { slug?: string[] } }) {
  return (
    <div>
      <h1>Slug Test Page</h1>
      <p>Received slug: {JSON.stringify(params.slug)}</p>
      <p>Slug as array: {JSON.stringify(params.slug?.map(decodeURIComponent))}</p>
    </div>
  )
}
