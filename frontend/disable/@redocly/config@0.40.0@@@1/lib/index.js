var __createBinding =
	(this && this.__createBinding) ||
	(Object.create
		? (o, m, k, k2) => {
				if (k2 === undefined) k2 = k;
				var desc = Object.getOwnPropertyDescriptor(m, k);
				if (
					!desc ||
					("get" in desc ? !m.__esModule : desc.writable || desc.configurable)
				) {
					desc = {
						enumerable: true,
						get: () => m[k],
					};
				}
				Object.defineProperty(o, k2, desc);
			}
		: (o, m, k, k2) => {
				if (k2 === undefined) k2 = k;
				o[k2] = m[k];
			});
var __exportStar =
	(this && this.__exportStar) ||
	((m, exports) => {
		for (var p in m)
			if (p !== "default" && !Object.hasOwn(exports, p))
				__createBinding(exports, m, p);
	});
Object.defineProperty(exports, "__esModule", { value: true });
exports.ENTITY_RELATION_TYPES =
	exports.REDOCLY_ROUTE_RBAC =
	exports.REDOCLY_TEAMS_RBAC =
	exports.LayoutVariant =
	exports.DEFAULT_TEAM_CLAIM_NAME =
	exports.AuthProviderType =
	exports.ApigeeDevOnboardingIntegrationAuthType =
	exports.redocConfigSchema =
	exports.rootRedoclyConfigSchema =
	exports.rbacConfigSchema =
	exports.productConfigOverrideSchema =
	exports.productThemeOverrideSchema =
		void 0;
var product_override_schema_1 = require("./product-override-schema");
Object.defineProperty(exports, "productThemeOverrideSchema", {
	enumerable: true,
	get: () => product_override_schema_1.productThemeOverrideSchema,
});
Object.defineProperty(exports, "productConfigOverrideSchema", {
	enumerable: true,
	get: () => product_override_schema_1.productConfigOverrideSchema,
});
var root_config_schema_1 = require("./root-config-schema");
Object.defineProperty(exports, "rbacConfigSchema", {
	enumerable: true,
	get: () => root_config_schema_1.rbacConfigSchema,
});
Object.defineProperty(exports, "rootRedoclyConfigSchema", {
	enumerable: true,
	get: () => root_config_schema_1.rootRedoclyConfigSchema,
});
var redoc_config_schema_1 = require("./redoc-config-schema");
Object.defineProperty(exports, "redocConfigSchema", {
	enumerable: true,
	get: () => redoc_config_schema_1.redocConfigSchema,
});
__exportStar(require("./types"), exports);
__exportStar(require("./common"), exports);
var constants_1 = require("./constants");
Object.defineProperty(exports, "ApigeeDevOnboardingIntegrationAuthType", {
	enumerable: true,
	get: () => constants_1.ApigeeDevOnboardingIntegrationAuthType,
});
Object.defineProperty(exports, "AuthProviderType", {
	enumerable: true,
	get: () => constants_1.AuthProviderType,
});
Object.defineProperty(exports, "DEFAULT_TEAM_CLAIM_NAME", {
	enumerable: true,
	get: () => constants_1.DEFAULT_TEAM_CLAIM_NAME,
});
Object.defineProperty(exports, "LayoutVariant", {
	enumerable: true,
	get: () => constants_1.LayoutVariant,
});
Object.defineProperty(exports, "REDOCLY_TEAMS_RBAC", {
	enumerable: true,
	get: () => constants_1.REDOCLY_TEAMS_RBAC,
});
Object.defineProperty(exports, "REDOCLY_ROUTE_RBAC", {
	enumerable: true,
	get: () => constants_1.REDOCLY_ROUTE_RBAC,
});
Object.defineProperty(exports, "ENTITY_RELATION_TYPES", {
	enumerable: true,
	get: () => constants_1.ENTITY_RELATION_TYPES,
});
__exportStar(require("./entities-catalog-entity-file-schema"), exports);
//# sourceMappingURL=index.js.map
