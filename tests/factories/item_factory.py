"""Item factory for generating test items with realistic data.

Uses faker for data generation and provides automatic cleanup.
"""

from typing import Any

from faker import Faker

fake = Faker()


class ItemFactory:
    """Factory for creating test items.

    Example:
        >>> factory = ItemFactory(session=db_session)
        >>> item = factory.create(title="Test Feature", view="FEATURE")
        >>> items = factory.create_batch(10, view="CODE")
    """

    def __init__(self, session: Any = None) -> None:
        """Initialize factory with optional database session.

        Args:
            session: SQLAlchemy session for database operations
        """
        self.session = session
        self.created_items = []

    def create(
        self,
        title: str | None = None,
        description: str | None = None,
        view: str = "FEATURE",
        item_type: str = "feature",
        status: str = "todo",
        **kwargs: Any,
    ) -> None:
        """Create a single test item.

        Args:
            title: Item title (auto-generated if None)
            description: Item description (auto-generated if None)
            view: View name (FEATURE, CODE, TEST, etc.)
            item_type: Item type (feature, story, task, etc.)
            status: Item status (todo, in_progress, done, etc.)
            **kwargs: Additional item attributes

        Returns:
            Created item instance
        """
        # Generate realistic test data
        if title is None:
            title = fake.catch_phrase()

        if description is None:
            description = fake.paragraph(nb_sentences=3)

        # Create item data
        item_data = {
            "title": title,
            "description": description,
            "view": view,
            "item_type": item_type,
            "status": status,
            "version": 1,
            **kwargs,
        }

        # If session provided, create in database
        if self.session:
            from tracertm.models import Item

            item = Item(**item_data)
            self.session.add(item)
            self.session.commit()
            self.created_items.append(item.id)
            return item

        # Otherwise return dict (for unit tests)
        return item_data

    def create_batch(self, count: int, **kwargs: Any) -> None:
        """Create multiple test items.

        Args:
            count: Number of items to create
            **kwargs: Attributes to apply to all items

        Returns:
            List of created items
        """
        return [self.create(**kwargs) for _ in range(count)]

    def create_hierarchy(self, depth: int = 3, children_per_level: int = 3) -> None:
        """Create a hierarchical structure of items.

        Args:
            depth: Number of levels in hierarchy
            children_per_level: Number of children per parent

        Returns:
            Root item with nested children
        """

        def create_level(parent_id: Any = None, current_depth: Any = 0) -> None:
            if current_depth >= depth:
                return []

            items = []
            for i in range(children_per_level):
                item = self.create(title=f"Level {current_depth} Item {i}", parent_id=parent_id)
                items.append(item)

                # Recursively create children
                if current_depth < depth - 1:
                    create_level(parent_id=item.get("id"), current_depth=current_depth + 1)

            return items

        root = self.create(title="Root Item")
        create_level(parent_id=root.get("id"), current_depth=1)
        return root

    def cleanup(self) -> None:
        """Delete all items created by this factory.

        Called automatically by pytest fixture after each test.
        """
        if self.session and self.created_items:
            from tracertm.models import Item

            self.session.query(Item).filter(Item.id.in_(self.created_items)).delete(synchronize_session=False)
            self.session.commit()
            self.created_items = []
