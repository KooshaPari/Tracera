import { useCallback, useEffect } from "react";

export const useOnClickOutside = <T extends HTMLElement = HTMLElement>(
	ref: React.RefObject<T>,
	handler: (event: MouseEvent | TouchEvent) => void,
): void => {
	const listener = useCallback(
		(event: MouseEvent | TouchEvent) => {
			const el = ref?.current;
			if (!el || el.contains(event.target as Node)) {
				return;
			}

			handler(event);
		},
		[handler, ref],
	);

	useEffect(() => {
		if (typeof document === "undefined") {
			return;
		}

		document.addEventListener("mousedown", listener);
		document.addEventListener("touchstart", listener);

		return () => {
			document.removeEventListener("mousedown", listener);
			document.removeEventListener("touchstart", listener);
		};
	}, [listener]);
};
