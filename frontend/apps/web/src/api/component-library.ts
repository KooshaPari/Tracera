import { componentLibraryMutations } from "./component-library.mutations";
import * as componentLibraryQueries from "./component-library.queries";

type ComponentLibraryApi = typeof componentLibraryQueries &
	typeof componentLibraryMutations;

const componentLibraryApi: ComponentLibraryApi = Object.assign(
	{},
	componentLibraryQueries,
	componentLibraryMutations,
);

export { componentLibraryApi };
