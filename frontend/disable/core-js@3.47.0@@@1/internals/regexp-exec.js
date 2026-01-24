"use strict";
/* eslint-disable regexp/no-empty-capturing-group, regexp/no-empty-group, regexp/no-lazy-ends -- testing */
/* eslint-disable regexp/no-useless-quantifier -- testing */
var call = require("../internals/function-call");
var uncurryThis = require("../internals/function-uncurry-this");
var toString = require("../internals/to-string");
var regexpFlags = require("../internals/regexp-flags");
var stickyHelpers = require("../internals/regexp-sticky-helpers");
var shared = require("../internals/shared");
var create = require("../internals/object-create");
var getInternalState = require("../internals/internal-state").get;
var UNSUPPORTED_DOT_ALL = require("../internals/regexp-unsupported-dot-all");
var UNSUPPORTED_NCG = require("../internals/regexp-unsupported-ncg");

var nativeReplace = shared("native-string-replace", String.prototype.replace);
var nativeExec = RegExp.prototype.exec;
var patchedExec = nativeExec;
var charAt = uncurryThis("".charAt);
var indexOf = uncurryThis("".indexOf);
var replace = uncurryThis("".replace);
var stringSlice = uncurryThis("".slice);

var UPDATES_LAST_INDEX_WRONG = (() => {
	var re1 = /a/;
	var re2 = /b*/g;
	call(nativeExec, re1, "a");
	call(nativeExec, re2, "a");
	return re1.lastIndex !== 0 || re2.lastIndex !== 0;
})();

var UNSUPPORTED_Y = stickyHelpers.BROKEN_CARET;

// nonparticipating capturing group, copied from es5-shim's String#split patch.
var NPCG_INCLUDED = /()??/.exec("")[1] !== undefined;

var PATCH =
	UPDATES_LAST_INDEX_WRONG ||
	NPCG_INCLUDED ||
	UNSUPPORTED_Y ||
	UNSUPPORTED_DOT_ALL ||
	UNSUPPORTED_NCG;

if (PATCH) {
	patchedExec = function exec(string) {
		var state = getInternalState(this);
		var str = toString(string);
		var raw = state.raw;
		var result, reCopy, lastIndex, match, i, object, group;

		if (raw) {
			raw.lastIndex = this.lastIndex;
			result = call(patchedExec, raw, str);
			this.lastIndex = raw.lastIndex;
			return result;
		}

		var groups = state.groups;
		var sticky = UNSUPPORTED_Y && this.sticky;
		var flags = call(regexpFlags, this);
		var source = this.source;
		var charsAdded = 0;
		var strCopy = str;

		if (sticky) {
			flags = replace(flags, "y", "");
			if (indexOf(flags, "g") === -1) {
				flags += "g";
			}

			strCopy = stringSlice(str, this.lastIndex);
			// Support anchored sticky behavior.
			if (
				this.lastIndex > 0 &&
				(!this.multiline ||
					(this.multiline && charAt(str, this.lastIndex - 1) !== "\n"))
			) {
				source = "(?: " + source + ")";
				strCopy = " " + strCopy;
				charsAdded++;
			}
			// ^(? + rx + ) is needed, in combination with some str slicing, to
			// simulate the 'y' flag.
			reCopy = new RegExp("^(?:" + source + ")", flags);
		}

		if (NPCG_INCLUDED) {
			reCopy = new RegExp("^" + source + "$(?!\\s)", flags);
		}
		if (UPDATES_LAST_INDEX_WRONG) lastIndex = this.lastIndex;

		match = call(nativeExec, sticky ? reCopy : this, strCopy);

		if (sticky) {
			if (match) {
				match.input = stringSlice(match.input, charsAdded);
				match[0] = stringSlice(match[0], charsAdded);
				match.index = this.lastIndex;
				this.lastIndex += match[0].length;
			} else this.lastIndex = 0;
		} else if (UPDATES_LAST_INDEX_WRONG && match) {
			this.lastIndex = this.global ? match.index + match[0].length : lastIndex;
		}
		if (NPCG_INCLUDED && match && match.length > 1) {
			// Fix browsers whose `exec` methods don't consistently return `undefined`
			// for NPCG, like IE8. NOTE: This doesn't work for /(.?)?/
			call(nativeReplace, match[0], reCopy, function () {
				for (i = 1; i < arguments.length - 2; i++) {
					if (arguments[i] === undefined) match[i] = undefined;
				}
			});
		}

		if (match && groups) {
			match.groups = object = create(null);
			for (i = 0; i < groups.length; i++) {
				group = groups[i];
				object[group[0]] = match[group[1]];
			}
		}

		return match;
	};
}

module.exports = patchedExec;
