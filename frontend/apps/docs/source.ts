import type { MetaData, PageData } from 'fumadocs-core/source';
import type { DocCollectionEntry, MetaCollectionEntry } from 'fumadocs-mdx/runtime/server';

import { loader } from 'fumadocs-core/source';
import { toFumadocsSource } from 'fumadocs-mdx/runtime/server';

import { docs, meta } from './.source/server';

type DocFrontmatter = PageData & {
  full?: boolean;
  index?: boolean;
  _openapi?: Record<string, unknown>;
};

const fumadocsSource = toFumadocsSource(
  docs as DocCollectionEntry<'docs', DocFrontmatter>[],
  meta as MetaCollectionEntry<MetaData>[],
);

export const source = loader({
  baseUrl: '/docs',
  source: fumadocsSource,
});
