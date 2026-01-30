# QA Integration - Frontend Integration Guide

This guide explains how to integrate the QA Integration components into your React Flow graph.

---

## Quick Start

### 1. Using QAEnhancedNode in React Flow

```tsx
import { QAEnhancedNode, type QAEnhancedNodeData } from "@tracertm/web/components/graph";
import { useQAEnhancedNodeData } from "@tracertm/web/hooks";
import { ReactFlow, NodeTypes } from "@xyflow/react";

// Register node types
const nodeTypes: NodeTypes = {
  richPill: RichNodePill,  // Existing
  qaEnhanced: QAEnhancedNode,  // New QA node
};

function MyGraphView({ items, projectId }: Props) {
  // Transform items to nodes with QA data
  const nodes = items.map((item) => {
    const qaData = useQAEnhancedNodeData({
      projectId,
      itemId: item.id,
    });

    return {
      id: item.id,
      type: qaData.metrics || qaData.preview ? "qaEnhanced" : "richPill",
      position: { x: 0, y: 0 }, // Calculate from layout
      data: {
        id: item.id,
        item,
        label: item.title,
        type: item.type,
        status: item.status,
        connections: { incoming: 0, outgoing: 0, total: 0 },
        // QA-specific data
        metrics: qaData.metrics,
        preview: qaData.preview,
        artifacts: qaData.artifacts,
      } as QAEnhancedNodeData,
    };
  });

  return <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} />;
}
```

### 2. Creating Executions

```tsx
import { useCreateExecution, useStartExecution } from "@tracertm/web/hooks";

function RunTestsButton({ projectId, itemId }: Props) {
  const createExecution = useCreateExecution(projectId);
  const startExecution = useStartExecution(projectId);

  const handleRunVHS = async () => {
    // Create execution
    const execution = await createExecution.mutateAsync({
      execution_type: "vhs",
      trigger_source: "manual",
      item_id: itemId,
      config: {
        commands: ["npm test", "npm run coverage"],
      },
    });

    // Start execution
    await startExecution.mutateAsync(execution.id);
  };

  return <Button onClick={handleRunVHS}>Run VHS Demo</Button>;
}
```

### 3. Using Codex Agent

```tsx
import { useCodexReviewImage, useCodexAuthStatus } from "@tracertm/web/hooks";

function ReviewArtifactButton({ projectId, artifactId }: Props) {
  const reviewImage = useCodexReviewImage(projectId);
  const { data: authStatus } = useCodexAuthStatus(projectId);

  const handleReview = async () => {
    if (!authStatus?.authenticated) {
      alert("Please authenticate Codex CLI first: codex login");
      return;
    }

    const result = await reviewImage.mutateAsync({
      artifact_id: artifactId,
      prompt: "Review this screenshot for UI issues and accessibility concerns",
    });

    console.log("Codex review:", result.response);
  };

  return (
    <Button onClick={handleReview} disabled={!authStatus?.authenticated}>
      Review with Codex
    </Button>
  );
}
```

---

## API Endpoints Reference

### Executions

- `POST /api/v1/projects/{project_id}/executions` - Create execution
- `GET /api/v1/projects/{project_id}/executions` - List executions
- `GET /api/v1/projects/{project_id}/executions/{execution_id}` - Get execution
- `POST /api/v1/projects/{project_id}/executions/{execution_id}/start` - Start execution
- `POST /api/v1/projects/{project_id}/executions/{execution_id}/complete` - Complete execution
- `GET /api/v1/projects/{project_id}/executions/{execution_id}/artifacts` - List artifacts
- `GET /api/v1/projects/{project_id}/executions/{execution_id}/artifacts/{artifact_id}/download` - Download artifact
- `GET /api/v1/projects/{project_id}/execution-config` - Get config
- `PUT /api/v1/projects/{project_id}/execution-config` - Update config

### Codex Agent

- `POST /api/v1/projects/{project_id}/codex/review-image` - Review image artifact
- `POST /api/v1/projects/{project_id}/codex/review-video` - Review video artifact
- `GET /api/v1/projects/{project_id}/codex/interactions` - List interactions
- `GET /api/v1/projects/{project_id}/codex/auth-status` - Check auth status

---

## React Hooks

### Execution Hooks

- `useExecutions(projectId, options?)` - List executions
- `useExecution(projectId, executionId)` - Get single execution
- `useExecutionArtifacts(projectId, executionId, artifactType?)` - List artifacts
- `useExecutionConfig(projectId)` - Get execution config
- `useCreateExecution(projectId)` - Create execution mutation
- `useStartExecution(projectId)` - Start execution mutation
- `useCompleteExecution(projectId)` - Complete execution mutation
- `useUpdateExecutionConfig(projectId)` - Update config mutation

### Codex Hooks

- `useCodexInteractions(projectId, options?)` - List Codex interactions
- `useCodexAuthStatus(projectId)` - Check Codex auth status
- `useCodexReviewImage(projectId)` - Review image mutation
- `useCodexReviewVideo(projectId)` - Review video mutation

### QA Node Data Hook

- `useQAEnhancedNodeData({ projectId, itemId })` - Fetch QA metrics/artifacts for a node

---

## Component Props

### QAEnhancedNode

```tsx
interface QAEnhancedNodeData {
  id: string;
  item: Item;
  label: string;
  type: string;
  status: string;
  description?: string;
  metrics?: QANodeMetrics;
  preview?: QANodePreview;
  artifacts?: QANodeArtifact[];
  connections: { incoming: number; outgoing: number; total: number };
  onExpandPopup?: (nodeId: string) => void;
  onRunTests?: (nodeId: string) => void;
}
```

### NodeExpandPopup

```tsx
interface NodeExpandPopupProps {
  data: QAEnhancedNodeData;
  onClose: () => void;
}
```

---

## Example: Full Integration

```tsx
import { QAEnhancedNode } from "@tracertm/web/components/graph";
import { useQAEnhancedNodeData, useCreateExecution } from "@tracertm/web/hooks";
import { ReactFlow, NodeTypes } from "@xyflow/react";

const nodeTypes: NodeTypes = {
  qaEnhanced: QAEnhancedNode,
};

function QAGraphView({ items, projectId }: Props) {
  return (
    <ReactFlow
      nodes={items.map((item) => {
        const qaData = useQAEnhancedNodeData({ projectId, itemId: item.id });
        return {
          id: item.id,
          type: "qaEnhanced",
          position: calculatePosition(item),
          data: {
            id: item.id,
            item,
            label: item.title,
            type: item.type,
            status: item.status,
            connections: calculateConnections(item),
            ...qaData,
          },
        };
      })}
      nodeTypes={nodeTypes}
    />
  );
}
```

---

## Next Steps

1. **Wire to GraphView**: Update `FlowGraphView.tsx` to conditionally use `qaEnhanced` node type when QA data exists
2. **Add Actions**: Implement `onRunTests` callback to trigger VHS/Playwright executions
3. **Real-time Updates**: Use WebSocket or polling to update execution status in real-time
4. **Artifact URLs**: Configure artifact base URL in environment variables

---

**All components are ready for integration!** 🚀
