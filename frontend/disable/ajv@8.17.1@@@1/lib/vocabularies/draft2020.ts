import type { Vocabulary } from "../types";
import getApplicatorVocabulary from "./applicator";
import coreVocabulary from "./core";
import dynamicVocabulary from "./dynamic";
import formatVocabulary from "./format";
import { contentVocabulary, metadataVocabulary } from "./metadata";
import nextVocabulary from "./next";
import unevaluatedVocabulary from "./unevaluated";
import validationVocabulary from "./validation";

const draft2020Vocabularies: Vocabulary[] = [
	dynamicVocabulary,
	coreVocabulary,
	validationVocabulary,
	getApplicatorVocabulary(true),
	formatVocabulary,
	metadataVocabulary,
	contentVocabulary,
	nextVocabulary,
	unevaluatedVocabulary,
];

export default draft2020Vocabularies;
