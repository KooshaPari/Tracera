import * as componentLibraryQueries from "./component-library.queries";
import { componentLibraryMutations } from "./component-library.mutations";

const componentLibraryApi = {};
Object.assign(componentLibraryApi, componentLibraryQueries, componentLibraryMutations);

export { componentLibraryApi };
