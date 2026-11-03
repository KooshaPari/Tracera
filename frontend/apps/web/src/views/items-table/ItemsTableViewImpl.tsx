import { useNavigate, useSearch } from "@tanstack/react-router";
import React from "react";
import { toast } from "sonner";

import type { Project, TypedItem, ViewType } from "@tracertm/types";

import { useCreateItem, useDeleteItem, useItems } from "@/hooks/useItems";
import { useProjects } from "@/hooks/useProjects";
import { Button } from "@tracertm/ui";

import type { CreateItemPayload } from "./create-item-modal";

import itemsTableConstants from "./constants";
import { CreateItemModal } from "./create-item-modal";
import itemsTableFormatters from "./formatters";
import { ItemsTableContent } from "./ItemsTableContent";
import { ItemsTableFiltersBar } from "./ItemsTableFiltersBar";
import { getViewLabels } from "./view-labels";

interface ItemsTableViewProps {
  projectId?: string | undefined;
  view?: ViewType | undefined;
  type?: string | undefined;
}

const EMPTY_ITEMS: TypedItem[] = [];
const PAGE_SIZE = 50;
const MAX_OFFSET = 100_000;

function isAccessDenied(error: unknown): boolean {
  return (
    error instanceof Error && "status" in error && (error.status === 401 || error.status === 403)
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

const mergeSearch = (prev: unknown, patch: Record<string, unknown>): Record<string, unknown> => {
  if (isRecord(prev)) {
    return { ...prev, ...patch };
  }
  return { ...patch };
};

function ItemsTableView({ projectId, view, type }: ItemsTableViewProps = {}): JSX.Element {
  const navigate = useNavigate();
  const search = useSearch({ strict: false });

  const projectFilter = itemsTableFormatters.getSearchValue(
    search,
    itemsTableConstants.SEARCH_PARAM_PROJECT,
  );
  const typeFilter = itemsTableFormatters.getSearchValue(
    search,
    itemsTableConstants.SEARCH_PARAM_TYPE,
  );
  const actionParam = itemsTableFormatters.getSearchValue(
    search,
    itemsTableConstants.SEARCH_PARAM_ACTION,
  );

  const effectiveProjectId = React.useMemo((): string | undefined => {
    if (itemsTableFormatters.hasValue(projectId)) {
      return projectId;
    }
    if (itemsTableFormatters.hasValue(projectFilter)) {
      return projectFilter;
    }
    return undefined;
  }, [projectFilter, projectId]);

  const effectiveTypeFilter = React.useMemo((): string | undefined => {
    if (itemsTableFormatters.hasValue(type)) {
      return type;
    }
    if (itemsTableFormatters.hasValue(typeFilter)) {
      return typeFilter;
    }
    return undefined;
  }, [type, typeFilter]);

  const pageScope = JSON.stringify([effectiveProjectId ?? null, view ?? null]);
  const [page, setPage] = React.useState({ scope: pageScope, offset: 0 });
  const offset = page.scope === pageScope ? page.offset : 0;
  React.useEffect(() => {
    setPage((previous) =>
      previous.scope === pageScope ? previous : { scope: pageScope, offset: 0 },
    );
  }, [pageScope]);
  const {
    data: itemsData,
    isLoading,
    isError,
    isFetching,
    error,
    refetch,
  } = useItems({
    projectId: effectiveProjectId,
    view,
    limit: PAGE_SIZE,
    offset,
  });
  const accessDenied = isError && isAccessDenied(error);
  const unsupported = (itemsData?.unsupportedFields?.length ?? 0) > 0;
  const items = accessDenied || unsupported ? EMPTY_ITEMS : (itemsData?.items ?? EMPTY_ITEMS);

  const { data: projects } = useProjects();
  const projectsArray: Project[] = Array.isArray(projects) ? projects : [];

  const deleteItem = useDeleteItem();
  const createItem = useCreateItem();

  const labels = React.useMemo(() => getViewLabels(view), [view]);

  const [showCreateModal, setShowCreateModal] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState<string>(itemsTableConstants.EMPTY_STRING);
  const [sortColumn, setSortColumn] = React.useState("created");
  const [sortOrder, setSortOrder] = React.useState<"asc" | "desc">("desc");
  const [showLoadingState, setShowLoadingState] = React.useState(false);
  const [liveMessage, setLiveMessage] = React.useState("Items loaded.");

  React.useEffect(() => {
    if (actionParam === itemsTableConstants.ACTION_CREATE) {
      setShowCreateModal(true);
    }
  }, [actionParam]);

  const closeCreateModal = React.useCallback((): void => {
    setShowCreateModal(false);
    if (actionParam !== itemsTableConstants.ACTION_CREATE) {
      return;
    }
    navigate({
      search: ((prev: unknown) =>
        mergeSearch(prev, { [itemsTableConstants.SEARCH_PARAM_ACTION]: undefined })) as never,
    });
  }, [actionParam, navigate]);

  const handleItemNavigate = React.useCallback(
    (item: TypedItem): void => {
      const projectIdValue = effectiveProjectId;
      if (projectIdValue === undefined) {
        return;
      }
      const viewSegment = itemsTableFormatters.getViewSegment(view, item.view);
      navigate({
        to: `/projects/${projectIdValue}/views/${viewSegment}/${item.id}`,
      });
    },
    [navigate, effectiveProjectId, view],
  );

  const handleDelete = React.useCallback(
    (id: string): void => {
      deleteItem.mutate(id, {
        onError: () => {
          toast.error("Purge failure");
        },
        onSuccess: () => {
          toast.success("Node purged from registry");
        },
      });
    },
    [deleteItem],
  );

  const handleRefresh = React.useCallback(async (): Promise<void> => {
    setLiveMessage("Loading items...");
    setShowLoadingState(true);
    try {
      const result = await refetch();
      setLiveMessage(result.isError ? "Refresh failed." : "Items loaded.");
    } catch {
      setLiveMessage("Refresh failed.");
    } finally {
      setShowLoadingState(false);
    }
  }, [refetch]);

  const handleProjectFilterChange = React.useCallback(
    (value: string): void => {
      const nextValue = itemsTableFormatters.getFilterValue(value);
      navigate({
        search: ((prev: unknown) =>
          mergeSearch(prev, { [itemsTableConstants.SEARCH_PARAM_PROJECT]: nextValue })) as never,
      });
    },
    [navigate],
  );

  const handleTypeFilterChange = React.useCallback(
    (value: string): void => {
      const nextValue = itemsTableFormatters.getFilterValue(value);
      navigate({
        search: ((prev: unknown) =>
          mergeSearch(prev, { [itemsTableConstants.SEARCH_PARAM_TYPE]: nextValue })) as never,
      });
    },
    [navigate],
  );

  const handleCreateModalOpen = React.useCallback((): void => {
    setShowCreateModal(true);
  }, []);

  const handleCreate = React.useCallback(
    (payload: CreateItemPayload): void => {
      const projectIdValue = effectiveProjectId;
      if (projectIdValue === undefined) {
        toast.error("Select a project before creating a node.");
        return;
      }

      const resolvedType = itemsTableFormatters.getItemTypeValue(payload.type, view);
      const resolvedView = itemsTableFormatters.getViewValue(view);

      createItem.mutate(
        {
          description: payload.description,
          priority: payload.priority,
          projectId: projectIdValue,
          status: payload.status,
          title: payload.title,
          type: resolvedType,
          view: resolvedView,
        },
        {
          onError: () => {
            toast.error("Failed to create node");
          },
          onSuccess: () => {
            toast.success("Node created");
            setLiveMessage("Item created.");
            closeCreateModal();
          },
        },
      );
    },
    [closeCreateModal, createItem, effectiveProjectId, view],
  );

  const liveMessageValue = itemsTableFormatters.getLiveMessage(liveMessage);

  const filteredAndSortedItems = React.useMemo(
    () =>
      itemsTableFormatters.getSortedItems(
        items,
        effectiveTypeFilter,
        searchQuery.trim().toLowerCase(),
        sortColumn,
        sortOrder,
      ),
    [items, effectiveTypeFilter, searchQuery, sortColumn, sortOrder],
  );

  const handleSearchQueryChange = React.useCallback((next: string): void => {
    setSearchQuery(next);
  }, []);

  const handleSortColumnChange = React.useCallback((next: string): void => {
    setSortColumn(next);
  }, []);

  const handleSortOrderChange = React.useCallback((next: "asc" | "desc"): void => {
    setSortOrder(next);
  }, []);

  return (
    <>
      <ItemsTableFiltersBar
        items={items}
        filteredCount={filteredAndSortedItems.length}
        labels={labels}
        projectId={projectId}
        type={type}
        projects={projectsArray}
        projectFilter={projectFilter}
        typeFilter={effectiveTypeFilter}
        searchQuery={searchQuery}
        isRefreshing={isFetching || showLoadingState}
        onSearchQueryChange={handleSearchQueryChange}
        onProjectFilterChange={handleProjectFilterChange}
        onTypeFilterChange={handleTypeFilterChange}
        onRefresh={handleRefresh}
        onCreate={handleCreateModalOpen}
      />

      {isError && (
        <div role="alert" className="mx-auto max-w-[1600px] px-6 text-destructive">
          {accessDenied
            ? "Access to items was denied. Sign in or check your permissions."
            : unsupported
              ? "Could not refresh, and cached items contain unsupported fields."
              : itemsData === undefined
                ? "Could not load items. Try refreshing."
                : "Could not refresh items. The displayed data may be stale."}
        </div>
      )}
      {unsupported && !isError && (
        <div role="alert" className="mx-auto max-w-[1600px] px-6 text-destructive">
          Items cannot be displayed because this view does not support some item fields:{" "}
          {itemsData?.unsupportedFields.join(", ")}.
        </div>
      )}
      {!unsupported &&
        !accessDenied &&
        itemsData !== undefined &&
        itemsData.total > itemsData.items.length && (
          <p className="mx-auto max-w-[1600px] px-6 text-sm text-muted-foreground">
            Search and filters apply only to loaded items on this page. Items may change between
            page requests.
          </p>
        )}

      {!unsupported && !accessDenied && (!isError || itemsData !== undefined) && (
        <ItemsTableContent
          filteredItems={filteredAndSortedItems}
          isLoading={isLoading}
          labels={labels}
          liveMessageValue={liveMessageValue}
          showLoadingState={showLoadingState}
          sortColumn={sortColumn}
          sortOrder={sortOrder}
          onSortColumnChange={handleSortColumnChange}
          onSortOrderChange={handleSortOrderChange}
          onNavigate={handleItemNavigate}
          onDelete={handleDelete}
          onCreate={handleCreateModalOpen}
        />
      )}

      {itemsData !== undefined && !isError && (itemsData.total > PAGE_SIZE || offset > 0) && (
        <nav
          aria-label="Items pages"
          className="mx-auto flex max-w-[1600px] items-center gap-3 px-6 pb-6"
        >
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={offset === 0 || isFetching}
            onClick={() => setPage({ scope: pageScope, offset: Math.max(0, offset - PAGE_SIZE) })}
          >
            Previous page
          </Button>
          <span>
            Page {Math.floor(offset / PAGE_SIZE) + 1}
            {!unsupported && ` · ${itemsData.total} total items`}
          </span>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={
              offset + PAGE_SIZE >= itemsData.total || offset + PAGE_SIZE > MAX_OFFSET || isFetching
            }
            onClick={() => setPage({ scope: pageScope, offset: offset + PAGE_SIZE })}
          >
            Next page
          </Button>
          {offset + PAGE_SIZE > MAX_OFFSET && itemsData.total > offset + PAGE_SIZE && (
            <span>Further pages exceed the server's paging limit.</span>
          )}
        </nav>
      )}

      {showCreateModal && (
        <CreateItemModal
          labels={labels}
          defaultType={itemsTableFormatters.getItemTypeValue(type, view)}
          pending={createItem.isPending}
          onClose={closeCreateModal}
          onCreate={handleCreate}
        />
      )}
    </>
  );
}

export { ItemsTableView };
export type { ItemsTableViewProps };
