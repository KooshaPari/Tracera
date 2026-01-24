//.CommonJS
var CSSOM = {
	CSSStyleSheet: require("./CSSStyleSheet").CSSStyleSheet,
	CSSRule: require("./CSSRule").CSSRule,
	CSSNestedDeclarations: require("./CSSNestedDeclarations")
		.CSSNestedDeclarations,
	CSSStyleRule: require("./CSSStyleRule").CSSStyleRule,
	CSSGroupingRule: require("./CSSGroupingRule").CSSGroupingRule,
	CSSConditionRule: require("./CSSConditionRule").CSSConditionRule,
	CSSMediaRule: require("./CSSMediaRule").CSSMediaRule,
	CSSContainerRule: require("./CSSContainerRule").CSSContainerRule,
	CSSSupportsRule: require("./CSSSupportsRule").CSSSupportsRule,
	CSSStyleDeclaration: require("./CSSStyleDeclaration").CSSStyleDeclaration,
	CSSKeyframeRule: require("./CSSKeyframeRule").CSSKeyframeRule,
	CSSKeyframesRule: require("./CSSKeyframesRule").CSSKeyframesRule,
	CSSScopeRule: require("./CSSScopeRule").CSSScopeRule,
	CSSLayerBlockRule: require("./CSSLayerBlockRule").CSSLayerBlockRule,
	CSSLayerStatementRule: require("./CSSLayerStatementRule")
		.CSSLayerStatementRule,
};
// Use cssstyle if available
try {
	CSSOM.CSSStyleDeclaration = require("cssstyle").CSSStyleDeclaration;
} catch (e) {
	// ignore
}
///CommonJS

/**
 * Produces a deep copy of stylesheet — the instance variables of stylesheet are copied recursively.
 * @param {CSSStyleSheet|CSSOM.CSSStyleSheet} stylesheet
 * @nosideeffects
 * @return {CSSOM.CSSStyleSheet}
 */
CSSOM.clone = function clone(stylesheet) {
	var cloned = new CSSOM.CSSStyleSheet();

	var rules = stylesheet.cssRules;
	if (!rules) {
		return cloned;
	}

	for (var i = 0, rulesLength = rules.length; i < rulesLength; i++) {
		var rule = rules[i];
		var ruleClone = (cloned.cssRules[i] = new rule.constructor());

		var style = rule.style;
		if (style) {
			var styleClone = (ruleClone.style = new CSSOM.CSSStyleDeclaration());
			for (var j = 0, styleLength = style.length; j < styleLength; j++) {
				var name = (styleClone[j] = style[j]);
				styleClone[name] = style[name];
				styleClone._importants[name] = style.getPropertyPriority(name);
			}
			styleClone.length = style.length;
		}

		if (Object.hasOwn(rule, "keyText")) {
			ruleClone.keyText = rule.keyText;
		}

		if (Object.hasOwn(rule, "selectorText")) {
			ruleClone.selectorText = rule.selectorText;
		}

		if (Object.hasOwn(rule, "mediaText")) {
			ruleClone.mediaText = rule.mediaText;
		}

		if (Object.hasOwn(rule, "supportsText")) {
			ruleClone.supports = rule.supports;
		}

		if (Object.hasOwn(rule, "conditionText")) {
			ruleClone.conditionText = rule.conditionText;
		}

		if (Object.hasOwn(rule, "layerName")) {
			ruleClone.layerName = rule.layerName;
		}

		if (Object.hasOwn(rule, "href")) {
			ruleClone.href = rule.href;
		}

		if (Object.hasOwn(rule, "name")) {
			ruleClone.name = rule.name;
		}

		if (Object.hasOwn(rule, "nameList")) {
			ruleClone.nameList = rule.nameList;
		}

		if (Object.hasOwn(rule, "cssRules")) {
			ruleClone.cssRules = clone(rule).cssRules;
		}
	}

	return cloned;
};

//.CommonJS
exports.clone = CSSOM.clone;
///CommonJS
