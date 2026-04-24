import type { Metadata } from 'next';

import { DocsBody, DocsDescription, DocsPage, DocsTitle } from 'fumadocs-ui/page';
import { notFound } from 'next/navigation';

import { mdxComponents } from '@/components/mdx-components';
import { source } from '@/source';

interface PageProps {
  params: Promise<{ slug?: string[] }>;
}

export default async function Page(props: PageProps) {
  const params = await props.params;
  const page = source.getPage(params.slug);

  if (!page) {
    notFound();
  }

  const MDX = page.data.body;

  return (
    <DocsPage
      toc={page.data.toc}
      full={page.data.full ?? false}
      tableOfContent={{
        single: false,
        style: 'clerk',
      }}
      breadcrumb={{
        enabled: true,
      }}
      editOnGithub={{
        owner: 'yourusername',
        path: `content/docs/${page.data.info.path}`,
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

  if (!page) {
    notFound();
  }

  return {
    description: page.data.description,
    openGraph: {
      description: page.data.description ?? '',
      title: page.data.title,
      type: 'article',
    },
    title: page.data.title,
    twitter: {
      card: 'summary_large_image',
      description: page.data.description ?? '',
      title: page.data.title,
    },
  };
}
