import type { Vocabulary } from "../types";
import getApplicatorVocabulary from "./applicator";
import coreVocabulary from "./core";
import formatVocabulary from "./format";
import { contentVocabulary, metadataVocabulary } from "./metadata";
import validationVocabulary from "./validation";

const draft7Vocabularies: Vocabulary[] = [
	coreVocabulary,
	validationVocabulary,
	getApplicatorVocabulary(),
	formatVocabulary,
	metadataVocabulary,
	contentVocabulary,
];

export default draft7Vocabularies;
