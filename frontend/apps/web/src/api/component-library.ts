import componentLibraryMutations from "./component-library.mutations";
import componentLibraryQueries from "./component-library.queries";

// eslint-disable-next-line eslint/prefer-object-spread
const componentLibraryApi = Object.assign(
	{},
	componentLibraryQueries,
	componentLibraryMutations,
);

// eslint-disable-next-line import/no-default-export
export default componentLibraryApi;
