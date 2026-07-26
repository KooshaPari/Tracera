import { componentLibraryMutations } from './component-library.mutations';
import * as componentLibraryQueries from './component-library.queries';

type ComponentLibraryApi = typeof componentLibraryQueries & typeof componentLibraryMutations;

const componentLibraryApi: ComponentLibraryApi = {
  ...componentLibraryQueries,
  ...componentLibraryMutations,
};

export { componentLibraryApi };
