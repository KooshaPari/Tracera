/**
 * Browser-visible deployment sites for the deployment dashboard.
 *
 * These targets intentionally remain distinct from API_ORIGIN: an API gateway
 * is not necessarily a user-facing application URL.
 */
export type DeploymentEnvironment = "production" | "staging" | "development";

export type DeploymentSiteUrls = Record<DeploymentEnvironment, string | undefined>;

type DeploymentSiteEnv = {
  VITE_DEPLOYMENT_URL_DEVELOPMENT?: string;
  VITE_DEPLOYMENT_URL_PRODUCTION?: string;
  VITE_DEPLOYMENT_URL_STAGING?: string;
};

const normalizeDeploymentUrl = (value: string | undefined): string | undefined => {
  const candidate = value?.trim();
  if (!candidate) {
    return undefined;
  }

  try {
    const url = new URL(candidate);
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      return undefined;
    }

    return url.toString().replace(/\/$/, "");
  } catch {
    return undefined;
  }
};

export const getDeploymentSiteUrls = (env: DeploymentSiteEnv): DeploymentSiteUrls => ({
  development: normalizeDeploymentUrl(env.VITE_DEPLOYMENT_URL_DEVELOPMENT),
  production: normalizeDeploymentUrl(env.VITE_DEPLOYMENT_URL_PRODUCTION),
  staging: normalizeDeploymentUrl(env.VITE_DEPLOYMENT_URL_STAGING),
});

export const DEPLOYMENT_SITE_URLS = getDeploymentSiteUrls(import.meta.env);
