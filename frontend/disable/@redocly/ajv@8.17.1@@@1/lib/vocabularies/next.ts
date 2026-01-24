import type { Vocabulary } from "../types";
import dependentSchemas from "./applicator/dependentSchemas";
import dependentRequired from "./validation/dependentRequired";
import limitContains from "./validation/limitContains";

const next: Vocabulary = [dependentRequired, dependentSchemas, limitContains];

export default next;
