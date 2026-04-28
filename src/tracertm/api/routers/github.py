"""GitHub integration router - registers all GitHub endpoints."""

from fastapi import APIRouter

from tracertm.api.handlers import github_installations, github_projects, github_repositories
from tracertm.api.handlers.github_webhooks import receive_github_webhook
from tracertm.api.handlers.webhooks import github_app_webhook

router = APIRouter(prefix="/api/v1/integrations/github", tags=["github"])

# Repository endpoints
router.get("/repos")(github_repositories.list_github_repos)
router.post("/repos")(github_repositories.create_github_repo)
router.get("/repos/{owner}/{repo}/issues")(github_repositories.list_github_issues)

# GitHub App installation endpoints
router.get("/app/install-url")(github_installations.get_github_app_install_url)
router.post("/app/webhook")(github_app_webhook)
router.get("/app/installations")(github_installations.list_github_app_installations)
router.post("/app/installations/{installation_id}/link")(github_installations.link_github_app_installation)
router.delete("/app/installations/{installation_id}")(github_installations.delete_github_app_installation)

# GitHub Projects endpoints
router.get("/projects")(github_projects.list_github_projects)
router.post("/projects/auto-link")(github_projects.auto_link_github_projects)
router.get("/projects/linked")(github_projects.list_linked_github_projects)
router.delete("/projects/{github_project_id}/unlink")(github_projects.unlink_github_project)

# GitHub webhook endpoint (separate path)
webhook_router = APIRouter(prefix="/api/v1/webhooks/github", tags=["webhooks"])
webhook_router.post("/{webhook_id}")(receive_github_webhook)
