import { createLocalStorage } from "@solid-primitives/storage";
import { createMemo } from "solid-js";
import { THEME_PREFERENCE } from "./constants";
import type { Theme } from "./contexts";
import { PiPProvider, QueryDevtoolsContext, ThemeContext } from "./contexts";
import type { DevtoolsComponentType } from "./Devtools";
import { Devtools } from "./Devtools";
import { getPreferredColorScheme } from "./utils";

const DevtoolsComponent: DevtoolsComponentType = (props) => {
	const [localStore, setLocalStore] = createLocalStorage({
		prefix: "TanstackQueryDevtools",
	});

	const colorScheme = getPreferredColorScheme();

	const theme = createMemo(() => {
		const preference = (props.theme ||
			localStore.theme_preference ||
			THEME_PREFERENCE) as Theme;
		if (preference !== "system") return preference;
		return colorScheme();
	});

	return (
		<QueryDevtoolsContext.Provider value={props}>
			<PiPProvider localStore={localStore} setLocalStore={setLocalStore}>
				<ThemeContext.Provider value={theme}>
					<Devtools localStore={localStore} setLocalStore={setLocalStore} />
				</ThemeContext.Provider>
			</PiPProvider>
		</QueryDevtoolsContext.Provider>
	);
};

export default DevtoolsComponent;
