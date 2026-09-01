const renderButton = (): HTMLButtonElement => {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "Reload dashboard";
  button.setAttribute("aria-label", "Reload the dashboard after a startup failure");
  button.style.cssText = [
    "padding:8px 14px",
    "border-radius:8px",
    "border:1px solid #f59e0b",
    "background:#f59e0b",
    "color:#0b0f14",
    "font-weight:600",
    "cursor:pointer",
  ].join(";");
  button.addEventListener("click", () => globalThis.location.reload());
  return button;
};

/**
 * Render a safe terminal state when bootstrap fails outside React's error boundary.
 *
 * The entrypoint can reject before React mounts, so no React error boundary is
 * available. This renderer deliberately uses textContent and DOM APIs rather than
 * interpolating the caught error into HTML.
 */
export const renderFrontendStartupFailure = (): void => {
  const root = document.querySelector<HTMLElement>("#root");
  if (!root) {
    return;
  }

  const page = document.createElement("main");
  page.setAttribute("aria-labelledby", "startup-failure-heading");
  page.style.cssText = [
    "min-height:100vh",
    "display:flex",
    "align-items:center",
    "justify-content:center",
    "padding:24px",
    "background:#0b0f14",
    "color:#e6edf3",
    "font-family:ui-sans-serif,system-ui,-apple-system",
  ].join(";");

  const card = document.createElement("section");
  card.setAttribute("role", "alert");
  card.style.cssText = [
    "max-width:640px",
    "padding:32px",
    "border:1px solid rgba(239,68,68,0.45)",
    "border-radius:16px",
    "background:#0f1720",
  ].join(";");

  const heading = document.createElement("h1");
  heading.id = "startup-failure-heading";
  heading.textContent = "Dashboard startup failed";
  heading.style.cssText = "font-size:24px;margin:0 0 8px;color:#fca5a5;";

  const message = document.createElement("p");
  message.textContent =
    "Tracera could not finish starting. Reload the dashboard after the local services are available.";
  message.style.cssText = "margin:0 0 20px;color:#9aa4b2;line-height:1.5;";

  card.append(heading, message, renderButton());
  page.append(card);
  root.replaceChildren(page);
};
