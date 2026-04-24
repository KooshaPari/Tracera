// @ts-nocheck
import { default as __fd_glob_25 } from "../content/docs/03-api-reference/meta.json?collection=meta"
import { default as __fd_glob_24 } from "../content/docs/03-api-reference/openapi.yaml?collection=meta"
import { default as __fd_glob_23 } from "../content/docs/01-architecture/meta.json?collection=meta"
import { default as __fd_glob_22 } from "../content/docs/02-guides/meta.json?collection=meta"
import { default as __fd_glob_21 } from "../content/docs/00-getting-started/meta.json?collection=meta"
import { default as __fd_glob_20 } from "../content/docs/meta.json?collection=meta"
import * as __fd_glob_19 from "../content/docs/03-api-reference/index.mdx?collection=docs"
import * as __fd_glob_18 from "../content/docs/03-api-reference/01-auth.mdx?collection=docs"
import * as __fd_glob_17 from "../content/docs/01-architecture/cli-architecture.mdx?collection=docs"
import * as __fd_glob_16 from "../content/docs/01-architecture/frontend-architecture.mdx?collection=docs"
import * as __fd_glob_15 from "../content/docs/01-architecture/index.mdx?collection=docs"
import * as __fd_glob_14 from "../content/docs/01-architecture/backend-architecture.mdx?collection=docs"
import * as __fd_glob_13 from "../content/docs/02-guides/development.mdx?collection=docs"
import * as __fd_glob_12 from "../content/docs/02-guides/mcp-tools.mdx?collection=docs"
import * as __fd_glob_11 from "../content/docs/02-guides/deployment.mdx?collection=docs"
import * as __fd_glob_10 from "../content/docs/02-guides/migration.mdx?collection=docs"
import * as __fd_glob_9 from "../content/docs/02-guides/config-precedence.mdx?collection=docs"
import * as __fd_glob_8 from "../content/docs/02-guides/testing.mdx?collection=docs"
import * as __fd_glob_7 from "../content/docs/02-guides/index.mdx?collection=docs"
import * as __fd_glob_6 from "../content/docs/02-guides/database.mdx?collection=docs"
import * as __fd_glob_5 from "../content/docs/00-getting-started/onboarding.mdx?collection=docs"
import * as __fd_glob_4 from "../content/docs/00-getting-started/cli-tutorial.mdx?collection=docs"
import * as __fd_glob_3 from "../content/docs/00-getting-started/contributing.mdx?collection=docs"
import * as __fd_glob_2 from "../content/docs/00-getting-started/index.mdx?collection=docs"
import * as __fd_glob_1 from "../content/docs/00-getting-started/quick-start.mdx?collection=docs"
import * as __fd_glob_0 from "../content/docs/index.mdx?collection=docs"
import { server } from 'fumadocs-mdx/runtime/server';
import type * as Config from '../source.config';

const create = server<typeof Config, import("fumadocs-mdx/runtime/types").InternalTypeConfig & {
  DocData: {
  }
}>({"doc":{"passthroughs":["extractedReferences"]}});

export const docs = await create.doc("docs", "content/docs", {"index.mdx": __fd_glob_0, "00-getting-started/quick-start.mdx": __fd_glob_1, "00-getting-started/index.mdx": __fd_glob_2, "00-getting-started/contributing.mdx": __fd_glob_3, "00-getting-started/cli-tutorial.mdx": __fd_glob_4, "00-getting-started/onboarding.mdx": __fd_glob_5, "02-guides/database.mdx": __fd_glob_6, "02-guides/index.mdx": __fd_glob_7, "02-guides/testing.mdx": __fd_glob_8, "02-guides/config-precedence.mdx": __fd_glob_9, "02-guides/migration.mdx": __fd_glob_10, "02-guides/deployment.mdx": __fd_glob_11, "02-guides/mcp-tools.mdx": __fd_glob_12, "02-guides/development.mdx": __fd_glob_13, "01-architecture/backend-architecture.mdx": __fd_glob_14, "01-architecture/index.mdx": __fd_glob_15, "01-architecture/frontend-architecture.mdx": __fd_glob_16, "01-architecture/cli-architecture.mdx": __fd_glob_17, "03-api-reference/01-auth.mdx": __fd_glob_18, "03-api-reference/index.mdx": __fd_glob_19, });

export const meta = await create.meta("meta", "content/docs", {"meta.json": __fd_glob_20, "00-getting-started/meta.json": __fd_glob_21, "02-guides/meta.json": __fd_glob_22, "01-architecture/meta.json": __fd_glob_23, "03-api-reference/openapi.yaml": __fd_glob_24, "03-api-reference/meta.json": __fd_glob_25, });