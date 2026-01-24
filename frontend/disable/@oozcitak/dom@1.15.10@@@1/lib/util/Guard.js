Object.defineProperty(exports, "__esModule", { value: true });
var interfaces_1 = require("../dom/interfaces");
/**
 * Contains user-defined type guards for DOM objects.
 */
var Guard = /** @class */ (() => {
	function Guard() {}
	/**
	 * Determines if the given object is a `Node`.
	 *
	 * @param a - the object to check
	 */
	Guard.isNode = (a) => !!a && a._nodeType !== undefined;
	/**
	 * Determines if the given object is a `Document`.
	 *
	 * @param a - the object to check
	 */
	Guard.isDocumentNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.Document;
	/**
	 * Determines if the given object is a `DocumentType`.
	 *
	 * @param a - the object to check
	 */
	Guard.isDocumentTypeNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.DocumentType;
	/**
	 * Determines if the given object is a `DocumentFragment`.
	 *
	 * @param a - the object to check
	 */
	Guard.isDocumentFragmentNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.DocumentFragment;
	/**
	 * Determines if the given object is a `Attr`.
	 *
	 * @param a - the object to check
	 */
	Guard.isAttrNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.Attribute;
	/**
	 * Determines if the given node is a `CharacterData` node.
	 *
	 * @param a - the object to check
	 */
	Guard.isCharacterDataNode = (a) => {
		if (!Guard.isNode(a)) return false;
		var type = a._nodeType;
		return (
			type === interfaces_1.NodeType.Text ||
			type === interfaces_1.NodeType.ProcessingInstruction ||
			type === interfaces_1.NodeType.Comment ||
			type === interfaces_1.NodeType.CData
		);
	};
	/**
	 * Determines if the given object is a `Text` or a `CDATASection`.
	 *
	 * @param a - the object to check
	 */
	Guard.isTextNode = (a) =>
		Guard.isNode(a) &&
		(a._nodeType === interfaces_1.NodeType.Text ||
			a._nodeType === interfaces_1.NodeType.CData);
	/**
	 * Determines if the given object is a `Text`.
	 *
	 * @param a - the object to check
	 */
	Guard.isExclusiveTextNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.Text;
	/**
	 * Determines if the given object is a `CDATASection`.
	 *
	 * @param a - the object to check
	 */
	Guard.isCDATASectionNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.CData;
	/**
	 * Determines if the given object is a `Comment`.
	 *
	 * @param a - the object to check
	 */
	Guard.isCommentNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.Comment;
	/**
	 * Determines if the given object is a `ProcessingInstruction`.
	 *
	 * @param a - the object to check
	 */
	Guard.isProcessingInstructionNode = (a) =>
		Guard.isNode(a) &&
		a._nodeType === interfaces_1.NodeType.ProcessingInstruction;
	/**
	 * Determines if the given object is an `Element`.
	 *
	 * @param a - the object to check
	 */
	Guard.isElementNode = (a) =>
		Guard.isNode(a) && a._nodeType === interfaces_1.NodeType.Element;
	/**
	 * Determines if the given object is a custom `Element`.
	 *
	 * @param a - the object to check
	 */
	Guard.isCustomElementNode = (a) =>
		Guard.isElementNode(a) && a._customElementState === "custom";
	/**
	 * Determines if the given object is a `ShadowRoot`.
	 *
	 * @param a - the object to check
	 */
	Guard.isShadowRoot = (a) => !!a && a.host !== undefined;
	/**
	 * Determines if the given object is a `MouseEvent`.
	 *
	 * @param a - the object to check
	 */
	Guard.isMouseEvent = (a) =>
		!!a && a.screenX !== undefined && a.screenY != undefined;
	/**
	 * Determines if the given object is a slotable.
	 *
	 * Element and Text nodes are slotables. A slotable has an associated name
	 * (a string).
	 *
	 * @param a - the object to check
	 */
	Guard.isSlotable = (a) =>
		!!a &&
		a._name !== undefined &&
		a._assignedSlot !== undefined &&
		(Guard.isTextNode(a) || Guard.isElementNode(a));
	/**
	 * Determines if the given object is a slot.
	 *
	 * @param a - the object to check
	 */
	Guard.isSlot = (a) =>
		!!a &&
		a._name !== undefined &&
		a._assignedNodes !== undefined &&
		Guard.isElementNode(a);
	/**
	 * Determines if the given object is a `Window`.
	 *
	 * @param a - the object to check
	 */
	Guard.isWindow = (a) => !!a && a.navigator !== undefined;
	/**
	 * Determines if the given object is an `EventListener`.
	 *
	 * @param a - the object to check
	 */
	Guard.isEventListener = (a) => !!a && a.handleEvent !== undefined;
	/**
	 * Determines if the given object is a `RegisteredObserver`.
	 *
	 * @param a - the object to check
	 */
	Guard.isRegisteredObserver = (a) =>
		!!a && a.observer !== undefined && a.options !== undefined;
	/**
	 * Determines if the given object is a `TransientRegisteredObserver`.
	 *
	 * @param a - the object to check
	 */
	Guard.isTransientRegisteredObserver = (a) =>
		!!a && a.source !== undefined && Guard.isRegisteredObserver(a);
	return Guard;
})();
exports.Guard = Guard;
//# sourceMappingURL=Guard.js.map
