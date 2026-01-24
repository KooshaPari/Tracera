import { RouterProvider } from "@tanstack/react-router";
import type { AnyRouter } from "@tanstack/router-core";
import * as React from "react";

export function StartServer<TRouter extends AnyRouter>(props: {
	router: TRouter;
}) {
	return <RouterProvider router={props.router} />;
}
