export {
	/**
	 * @deprecated use `@trpc/react-query/server` instead
	 */
	type CreateSSGHelpersOptions,
	/**
	 * @deprecated use `import { createServerSideHelpers } from "@trpc/react-query/server"`
	 */
	createServerSideHelpers as createProxySSGHelpers,
	/**
	 * @deprecated use `@trpc/react-query/server` instead
	 */
	type DecoratedProcedureSSGRecord,
} from "../server";

export { createSSGHelpers } from "./ssg";
