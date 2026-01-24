"use strict";

exports.__esModule = true;
exports.YamlStyleGroup = exports.YamlStyle = void 0;
/**
 * @public
 */
const YamlStyle = (exports.YamlStyle = /*#__PURE__*/ ((YamlStyle) => {
	YamlStyle["Plain"] = "Plain";
	YamlStyle["SingleQuoted"] = "SingleQuoted";
	YamlStyle["DoubleQuoted"] = "DoubleQuoted";
	YamlStyle["Literal"] = "Literal";
	YamlStyle["Folded"] = "Folded";
	YamlStyle["Explicit"] = "Explicit";
	YamlStyle["SinglePair"] = "SinglePair";
	YamlStyle["NextLine"] = "NextLine";
	YamlStyle["InLine"] = "InLine";
	return YamlStyle;
})({}));
/**
 * @public
 */
const YamlStyleGroup = (exports.YamlStyleGroup = /*#__PURE__*/ ((
	YamlStyleGroup,
) => {
	YamlStyleGroup["Flow"] = "Flow";
	YamlStyleGroup["Block"] = "Block";
	return YamlStyleGroup;
})({}));
