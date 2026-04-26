"""Main entry point."""
import uvicorn
from .infrastructure.config import settings


def main():
    """Run the application."""
    uvicorn.run(
        "src.interfaces.api.main:app",
        host="0.0.0.0",
        port=settings.http_port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    main()
