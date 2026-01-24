import type { DeferredPromise } from "@tanstack/router-core";

import { defer, TSR_DEFERRED_PROMISE } from "@tanstack/router-core";
import * as React from "react";

export type AwaitOptions<T> = {
	promise: Promise<T>;
};

/** Suspend until a deferred promise resolves/rejects and return its data. */
/** Suspend until a deferred promise resolves or rejects and return its data. */
export function useAwaited<T>({
	promise: _promise,
}: AwaitOptions<T>): [T, DeferredPromise<T>] {
	const promise = defer(_promise);

	if (promise[TSR_DEFERRED_PROMISE].status === "pending") {
		throw promise;
	}

	if (promise[TSR_DEFERRED_PROMISE].status === "error") {
		throw promise[TSR_DEFERRED_PROMISE].error;
	}

	return [promise[TSR_DEFERRED_PROMISE].data, promise];
}

/**
 * Component that suspends on a deferred promise and renders its child with
 * the resolved value. Optionally provides a Suspense fallback.
 */
/**
 * Component that suspends on a deferred promise and renders its child with
 * the resolved value. Optionally provides a Suspense fallback.
 */
export function Await<T>(
	props: AwaitOptions<T> & {
		fallback?: React.ReactNode;
		children: (result: T) => React.ReactNode;
	},
) {
	const inner = <AwaitInner {...props} />;
	if (props.fallback) {
		return <React.Suspense fallback={props.fallback}>{inner}</React.Suspense>;
	}
	return inner;
}

function AwaitInner<T>(
	props: AwaitOptions<T> & {
		fallback?: React.ReactNode;
		children: (result: T) => React.ReactNode;
	},
): React.JSX.Element {
	const [data] = useAwaited(props);

	return props.children(data) as React.JSX.Element;
}
