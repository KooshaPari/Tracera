import type { LayoutSignatureParams } from './types';

import { LAYOUT_SIGNATURE_SEPARATOR } from './constants';

export function buildSignature<NodeData extends Record<string, unknown>>({
  edges,
  layout,
  nodes,
}: LayoutSignatureParams<NodeData>): string {
  const nodeIds = nodes.map((node) => node.id).join(LAYOUT_SIGNATURE_SEPARATOR);
  const edgeIds = edges
    .map((edge) => `${edge.id}:${edge.source}->${edge.target}`)
    .join(LAYOUT_SIGNATURE_SEPARATOR);
  return `${layout}${LAYOUT_SIGNATURE_SEPARATOR}${nodeIds}${LAYOUT_SIGNATURE_SEPARATOR}${edgeIds}`;
}
