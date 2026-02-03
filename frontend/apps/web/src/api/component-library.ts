import { componentLibraryMutations } from "./component-library.mutations";
import * as componentLibraryQueries from "./component-library.queries";

const componentLibraryApi = {};
Object.assign(componentLibraryApi, componentLibraryQueries, componentLibraryMutations);

export { componentLibraryApi };
