"""
Project factory for generating test projects.
"""

from faker import Faker

fake = Faker()


class ProjectFactory:
    """Factory for creating test projects."""

    def __init__(self, session=None):
        self.session = session
        self.created_projects = []

    def create(self, name: str | None = None, description: str | None = None, **kwargs):
        """Create a single test project."""
        if name is None:
            name = fake.company() + " Project"

        if description is None:
            description = fake.paragraph()

        project_data = {"name": name, "description": description, **kwargs}

        if self.session:
            # Create in database
            pass

        return project_data

    def cleanup(self):
        """Delete all projects created by this factory."""
        if self.session and self.created_projects:
            self.created_projects = []
