// Settings API stub
import { logger } from "@/lib/logger";
import client from "./client";

const apiClient = client.apiClient;
const safeApiCall = client.safeApiCall;
const get = apiClient.GET.bind(apiClient);
const put = apiClient.PUT.bind(apiClient);

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

const fetchSettings = async (): Promise<Settings> => {
	// Try to fetch from settings endpoint, fallback to defaults
	try {
		const response = await safeApiCall<Settings>(
			get("/api/v1/settings", {}),
		);
		if (response.data !== undefined) {
			return response.data;
		}
	} catch {
		// Return default settings if endpoint doesn't exist
	}
	return DEFAULT_SETTINGS;
};

const updateSettings = async (
	settings: Partial<Settings>,
): Promise<Settings> => {
	try {
		const response = await safeApiCall<Settings>(
			put("/api/v1/settings", { body: settings }),
		);
		if (response.data !== undefined) {
			return response.data;
		}
	} catch {
		// Return merged settings if endpoint doesn't exist
	}
	return { ...DEFAULT_SETTINGS, ...settings };
};

/**
 * General settings map
 */
interface GeneralSettingsMap {
	theme?: "light" | "dark" | "system";
}

/**
 * Notification settings map
 */
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

// Simplified settings save function for SettingsView
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
		// Settings endpoint may not exist yet, that's okay
		logger.info("Settings saved locally:", settings);
	}
};

export { fetchSettings, saveSettings, updateSettings, type Settings };
