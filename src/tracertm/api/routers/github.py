"""GitHub integration router - registers all GitHub endpoints."""

from fastapi import APIRouter

from tracertm.api.handlers import github

router = APIRouter(prefix="/api/v1/integrations/github", tags=["github"])

# Repository endpoints
router.get("/repos")(github.list_github_repos)
router.post("/repos")(github.create_github_repo)
router.get("/repos/{owner}/{repo}/issues")(github.list_github_issues)

# GitHub App installation endpoints
router.get("/app/install-url")(github.get_github_app_install_url)
router.post("/app/webhook")(github.github_app_webhook)
router.get("/app/installations")(github.list_github_app_installations)
router.post("/app/installations/{installation_id}/link")(github.link_github_app_installation)
router.delete("/app/installations/{installation_id}")(github.delete_github_app_installation)

# GitHub Projects endpoints
router.get("/projects")(github.list_github_projects)
router.post("/projects/auto-link")(github.auto_link_github_projects)
router.get("/projects/linked")(github.list_linked_github_projects)
router.delete("/projects/{github_project_id}/unlink")(github.unlink_github_project)

# GitHub webhook endpoint (separate path)
webhook_router = APIRouter(prefix="/api/v1/webhooks/github", tags=["webhooks"])
webhook_router.post("/{webhook_id}")(github.receive_github_webhook)
