import { describe, expect, it } from "vitest";

import { getDeploymentSiteUrls } from "@/config/deployment-origin";

describe("getDeploymentSiteUrls", () => {
  it("maps each explicit deployment URL and removes a trailing slash", () => {
    expect(
      getDeploymentSiteUrls({
        VITE_DEPLOYMENT_URL_DEVELOPMENT: "https://dev.example.test/",
        VITE_DEPLOYMENT_URL_PRODUCTION: "https://app.example.test/",
        VITE_DEPLOYMENT_URL_STAGING: "https://staging.example.test/",
      }),
    ).toEqual({
      development: "https://dev.example.test",
      production: "https://app.example.test",
      staging: "https://staging.example.test",
    });
  });

  it("withholds missing or unsafe deployment URLs instead of inventing a target", () => {
    expect(
      getDeploymentSiteUrls({
        VITE_DEPLOYMENT_URL_DEVELOPMENT: "javascript:alert(1)",
        VITE_DEPLOYMENT_URL_PRODUCTION: "  ",
      }),
    ).toEqual({
      development: undefined,
      production: undefined,
      staging: undefined,
    });
  });
});
