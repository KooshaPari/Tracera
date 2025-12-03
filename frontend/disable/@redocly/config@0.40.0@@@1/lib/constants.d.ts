export declare const DEFAULT_TEAM_CLAIM_NAME = "https://redocly.com/sso/teams";
export declare enum AuthProviderType {
    OIDC = "OIDC",
    SAML2 = "SAML2"
}
export declare enum ApigeeDevOnboardingIntegrationAuthType {
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT",
    OAUTH2 = "OAUTH2"
}
export declare const REDOCLY_TEAMS_RBAC = "redocly::teams-rbac";
export declare const REDOCLY_ROUTE_RBAC = "redocly::route-rbac";
export declare enum LayoutVariant {
    STACKED = "stacked",
    THREE_PANEL = "three-panel"
}
export declare const ENTITY_RELATION_TYPES: readonly ["partOf", "hasParts", "creates", "createdBy", "owns", "ownedBy", "implements", "implementedBy", "dependsOn", "dependencyOf", "uses", "usedBy", "produces", "consumes", "linksTo", "supersedes", "supersededBy", "compatibleWith", "extends", "extendedBy", "relatesTo", "hasMember", "memberOf", "triggers", "triggeredBy", "returns", "returnedBy"];
