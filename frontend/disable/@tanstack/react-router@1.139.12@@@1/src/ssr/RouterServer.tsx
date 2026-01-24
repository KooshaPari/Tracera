import type { AnyRouter } from "@tanstack/router-core";
import * as React from "react";
import { RouterProvider } from "../RouterProvider";

export function RouterServer<TRouter extends AnyRouter>(props: {
	router: TRouter;
}) {
	return <RouterProvider router={props.router} />;
}
