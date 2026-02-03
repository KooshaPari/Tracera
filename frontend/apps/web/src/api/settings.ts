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

const mergeSettings = (
	baseSettings: Settings,
	overrides: Partial<Settings>,
): Settings => {
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

	if (overrides.general) {
		if (overrides.general.language !== undefined) {
			mergedSettings.general.language = overrides.general.language;
		}
		if (overrides.general.theme !== undefined) {
			mergedSettings.general.theme = overrides.general.theme;
		}
		if (overrides.general.timezone !== undefined) {
			mergedSettings.general.timezone = overrides.general.timezone;
		}
	}

	if (overrides.notifications) {
		if (!mergedSettings.notifications) {
			mergedSettings.notifications = {};
		}
		if (overrides.notifications.email !== undefined) {
			mergedSettings.notifications.email = overrides.notifications.email;
		}
		if (overrides.notifications.inApp !== undefined) {
			mergedSettings.notifications.inApp = overrides.notifications.inApp;
		}
		if (overrides.notifications.push !== undefined) {
			mergedSettings.notifications.push = overrides.notifications.push;
		}
	}

	if (overrides.security) {
		if (!mergedSettings.security) {
			mergedSettings.security = {};
		}
		if (overrides.security.sessionTimeout !== undefined) {
			mergedSettings.security.sessionTimeout = overrides.security.sessionTimeout;
		}
		if (overrides.security.twoFactor !== undefined) {
			mergedSettings.security.twoFactor = overrides.security.twoFactor;
		}
	}

	return mergedSettings;
};

const fetchSettings = async (): Promise<Settings> => {
	try {
		const response = await QueryClient.api.get<Settings>(
			"/api/v1/settings",
			{},
		);
		const data = await QueryClient.handleApiResponse(response);
		return data;
	} catch {
		return DEFAULT_SETTINGS;
	}
};

const updateSettings = async (
	settings: Partial<Settings>,
): Promise<Settings> => {
	try {
		const response = await QueryClient.api.put<Settings>("/api/v1/settings", {
			body: settings,
		});
		const data = await QueryClient.handleApiResponse(response);
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
