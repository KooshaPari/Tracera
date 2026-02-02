/* eslint-disable eslint/prefer-object-spread */
import componentLibraryMutationsLibrary from "./component-library-mutations-library";
import componentLibraryMutationsTokens from "./component-library-mutations-tokens";

const componentLibraryMutations = Object.assign(
	{},
	componentLibraryMutationsLibrary,
	componentLibraryMutationsTokens,
);

// eslint-disable-next-line import/no-default-export
export default componentLibraryMutations;
