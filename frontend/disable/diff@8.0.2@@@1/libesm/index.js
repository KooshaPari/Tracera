/* See LICENSE file for terms of use */
/*
 * Text diff implementation.
 *
 * This library supports the following APIs:
 * Diff.diffChars: Character by character diff
 * Diff.diffWords: Word (as defined by \b regex) diff which ignores whitespace
 * Diff.diffLines: Line based diff
 *
 * Diff.diffCss: Diff targeted at CSS content
 *
 * These methods are based on the implementation proposed in
 * "An O(ND) Difference Algorithm and its Variations" (Myers, 1986).
 * http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.4.6927
 */

import { convertChangesToDMP } from "./convert/dmp.js";
import { convertChangesToXML } from "./convert/xml.js";
import { arrayDiff, diffArrays } from "./diff/array.js";
import Diff from "./diff/base.js";
import { characterDiff, diffChars } from "./diff/character.js";
import { cssDiff, diffCss } from "./diff/css.js";
import { canonicalize, diffJson, jsonDiff } from "./diff/json.js";
import { diffLines, diffTrimmedLines, lineDiff } from "./diff/line.js";
import { diffSentences, sentenceDiff } from "./diff/sentence.js";
import {
	diffWords,
	diffWordsWithSpace,
	wordDiff,
	wordsWithSpaceDiff,
} from "./diff/word.js";
import { applyPatch, applyPatches } from "./patch/apply.js";
import {
	createPatch,
	createTwoFilesPatch,
	formatPatch,
	structuredPatch,
} from "./patch/create.js";
import { parsePatch } from "./patch/parse.js";
import { reversePatch } from "./patch/reverse.js";
export {
	Diff,
	diffChars,
	characterDiff,
	diffWords,
	wordDiff,
	diffWordsWithSpace,
	wordsWithSpaceDiff,
	diffLines,
	lineDiff,
	diffTrimmedLines,
	diffSentences,
	sentenceDiff,
	diffCss,
	cssDiff,
	diffJson,
	jsonDiff,
	diffArrays,
	arrayDiff,
	structuredPatch,
	createTwoFilesPatch,
	createPatch,
	formatPatch,
	applyPatch,
	applyPatches,
	parsePatch,
	reversePatch,
	convertChangesToDMP,
	convertChangesToXML,
	canonicalize,
};
