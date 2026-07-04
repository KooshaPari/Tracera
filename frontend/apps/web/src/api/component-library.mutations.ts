import { componentLibraryMutationsLibrary } from './component-library-mutations-library';
import { componentLibraryMutationsTokens } from './component-library-mutations-tokens';

const componentLibraryMutations = {};
Object.assign(
  componentLibraryMutations,
  componentLibraryMutationsLibrary,
  componentLibraryMutationsTokens,
);

export { componentLibraryMutations };
