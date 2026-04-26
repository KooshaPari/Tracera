"""Application handlers - orchestrate commands and queries."""
from uuid import UUID
from .commands import CreateCommand, UpdateCommand, DeleteCommand
from .queries import GetByIDQuery, ListQuery
from ..domain.entities import Example
from ..domain.errors import NotFoundError
from ..domain.ports import Repository, EventPublisher


class CommandHandler:
    """Handles CQRS commands."""

    def __init__(self, repo: Repository, publisher: EventPublisher | None = None):
        self._repo = repo
        self._publisher = publisher

    async def handle_create(self, cmd: CreateCommand) -> Example:
        """Handle create command."""
        example = Example(
            name=cmd.name.strip(),
            description=cmd.description.strip() if cmd.description else None,
        )
        example.validate()
        await self._repo.save(example)
        return example

    async def handle_update(self, cmd: UpdateCommand) -> Example:
        """Handle update command."""
        entity = await self._repo.find_by_id(cmd.id)
        if entity is None:
            raise NotFoundError(str(cmd.id))

        example = Example(
            id=cmd.id,
            name=cmd.name.strip(),
            description=cmd.description.strip() if cmd.description else None,
            created_at=entity.created_at,
        )
        example.validate()
        await self._repo.save(example)
        return example

    async def handle_delete(self, cmd: DeleteCommand) -> None:
        """Handle delete command."""
        await self._repo.delete(cmd.id)


class QueryHandler:
    """Handles CQRS queries."""

    def __init__(self, repo: Repository):
        self._repo = repo

    async def handle_get_by_id(self, query: GetByIDQuery) -> Example:
        """Handle get by ID query."""
        entity = await self._repo.find_by_id(query.id)
        if entity is None:
            raise NotFoundError(str(query.id))
        return entity

    async def handle_list(self, query: ListQuery) -> list[Example]:
        """Handle list query."""
        return await self._repo.list(page=query.page, page_size=query.page_size)
