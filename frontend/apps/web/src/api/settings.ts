import * as QueryClient from "./query-client";
import { logger } from "@/lib/logger";

interface Settings {
	general: {
		theme?: "light" | "dark" | "system";
		language?: string;
		timezone?: string;
	};
	notifications?: {
		email?: boolean;
		push?: boolean;
		inApp?: boolean;
	};
	security?: {
		twoFactor?: boolean;
		sessionTimeout?: number;
	};
}

const DEFAULT_SETTINGS: Settings = {
	general: {
		language: "en",
		theme: "system",
	},
	notifications: {
		email: true,
		inApp: true,
		push: true,
	},
	security: {
		sessionTimeout: 30,
		twoFactor: false,
	},
};

const isTheme = (value: unknown): value is "light" | "dark" | "system" =>
	value === "light" || value === "dark" || value === "system";

const createBaseSettings = (baseSettings: Settings): Settings => {
	const mergedSettings: Settings = {
		general: {
			language: baseSettings.general.language,
			theme: baseSettings.general.theme,
			timezone: baseSettings.general.timezone,
		},
	};

	if (baseSettings.notifications) {
		mergedSettings.notifications = {
			email: baseSettings.notifications.email,
			inApp: baseSettings.notifications.inApp,
			push: baseSettings.notifications.push,
		};
	}

	if (baseSettings.security) {
		mergedSettings.security = {
			sessionTimeout: baseSettings.security.sessionTimeout,
			twoFactor: baseSettings.security.twoFactor,
		};
	}

	return mergedSettings;
};

const applyGeneralOverrides = (
	target: Settings,
	overrides?: Settings["general"],
): void => {
	if (!overrides) {
		return;
	}
	if (overrides.language !== undefined) {
		target.general.language = overrides.language;
	}
	if (overrides.theme !== undefined) {
		target.general.theme = overrides.theme;
	}
	if (overrides.timezone !== undefined) {
		target.general.timezone = overrides.timezone;
	}
};

const applyNotificationOverrides = (
	target: Settings,
	overrides?: Settings["notifications"],
): void => {
	if (!overrides) {
		return;
	}
	if (!target.notifications) {
		target.notifications = {};
	}
	if (overrides.email !== undefined) {
		target.notifications.email = overrides.email;
	}
	if (overrides.inApp !== undefined) {
		target.notifications.inApp = overrides.inApp;
	}
	if (overrides.push !== undefined) {
		target.notifications.push = overrides.push;
	}
};

const applySecurityOverrides = (
	target: Settings,
	overrides?: Settings["security"],
): void => {
	if (!overrides) {
		return;
	}
	if (!target.security) {
		target.security = {};
	}
	if (overrides.sessionTimeout !== undefined) {
		target.security.sessionTimeout = overrides.sessionTimeout;
	}
	if (overrides.twoFactor !== undefined) {
		target.security.twoFactor = overrides.twoFactor;
	}
};

const mergeSettings = (
	baseSettings: Settings,
	overrides: Partial<Settings>,
): Settings => {
	const mergedSettings = createBaseSettings(baseSettings);
	applyGeneralOverrides(mergedSettings, overrides.general);
	applyNotificationOverrides(mergedSettings, overrides.notifications);
	applySecurityOverrides(mergedSettings, overrides.security);
	return mergedSettings;
};

const fetchSettings = async (): Promise<Settings> => {
	try {
		const response = QueryClient.api.get<Settings>("/api/v1/settings", {});
		const data = await QueryClient.handleApiResponse<Settings>(response);
		return data;
	} catch {
		return DEFAULT_SETTINGS;
	}
};

const updateSettings = async (
	settings: Partial<Settings>,
): Promise<Settings> => {
	try {
		const response = QueryClient.api.put<Settings>("/api/v1/settings", {
			body: settings,
		});
		const data = await QueryClient.handleApiResponse<Settings>(response);
		return data;
	} catch {
		return mergeSettings(DEFAULT_SETTINGS, settings);
	}
};

interface GeneralSettingsMap {
	theme?: "light" | "dark" | "system";
}

interface NotificationSettingsMap {
	email?: boolean;
	push?: boolean;
	inApp?: boolean;
}

const buildGeneralSettings = (settings: {
	theme?: string;
}): GeneralSettingsMap => {
	const generalSettings: GeneralSettingsMap = {};
	if (typeof settings.theme === "string" && isTheme(settings.theme)) {
		generalSettings.theme = settings.theme;
	}
	return generalSettings;
};

const buildNotificationSettings = (settings: {
	emailNotifications?: boolean;
	desktopNotifications?: boolean;
	weeklySummary?: boolean;
}): NotificationSettingsMap => {
	const notificationSettings: NotificationSettingsMap = {};
	if (settings.emailNotifications !== undefined) {
		notificationSettings.email = settings.emailNotifications;
	}
	if (settings.desktopNotifications !== undefined) {
		notificationSettings.push = settings.desktopNotifications;
	}
	if (settings.weeklySummary !== undefined) {
		notificationSettings.inApp = settings.weeklySummary;
	}
	return notificationSettings;
};

const saveSettings = async (settings: {
	displayName?: string;
	email?: string;
	theme?: string;
	fontSize?: string;
	emailNotifications?: boolean;
	desktopNotifications?: boolean;
	weeklySummary?: boolean;
}): Promise<void> => {
	try {
		const generalSettings = buildGeneralSettings(settings);
		const notificationSettings = buildNotificationSettings(settings);
		await updateSettings({
			general: generalSettings,
			notifications: notificationSettings,
		});
	} catch {
		logger.info("Settings saved locally:", settings);
	}
};

export { fetchSettings, saveSettings, updateSettings, type Settings };
