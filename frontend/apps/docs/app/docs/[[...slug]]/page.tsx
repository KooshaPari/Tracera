import type { Metadata } from 'next';
import { DocsBody, DocsDescription, DocsPage, DocsTitle } from 'fumadocs-ui/page';
import { notFound } from 'next/navigation';
import { source } from '@/source';
import { mdxComponents } from '@/components/mdx-components';

interface PageProps {
  params: Promise<{ slug?: string[] }>;
}

export default async function Page(props: PageProps) {
  const params = await props.params;
  const page = source.getPage(params.slug);

  if (!page) {notFound();}

  const MDX = page.data.body;

  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full}
      tableOfContent={{
        single: false,
        style: 'clerk',
      }}
      breadcrumb={{
        enabled: true,
      }}
      editOnGithub={{
        owner: 'yourusername',
        path: `content/docs/${page.file.path}`,
        repo: 'tracertm',
        sha: 'main',
      }}
    >
      <DocsTitle>{page.data.title}</DocsTitle>
      <DocsDescription>{page.data.description}</DocsDescription>
      <DocsBody>
        <MDX components={mdxComponents} />
      </DocsBody>
    </DocsPage>
  );
}

export async function generateStaticParams() {
  return source.generateParams();
}

export async function generateMetadata(props: PageProps): Promise<Metadata> {
  const params = await props.params;
  const page = source.getPage(params.slug);

  if (!page) {notFound();}

  return {
    description: page.data.description,
    openGraph: {
      title: page.data.title,
      description: page.data.description ?? '',
      type: 'article',
    },
    title: page.data.title,
    twitter: {
      card: 'summary_large_image',
      title: page.data.title,
      description: page.data.description ?? '',
    },
  };
}
