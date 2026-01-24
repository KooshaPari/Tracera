/*
The canvas renderer was written by Yue Dong.

Modifications tracked on Github.
*/

/* global OffscreenCanvas */

import * as is from "../../../is.mjs";
import { makeBoundingBox } from "../../../math.mjs";
import * as util from "../../../util/index.mjs";
import arrowShapes from "./arrow-shapes.mjs";
import drawingEdges from "./drawing-edges.mjs";
import drawingElements from "./drawing-elements.mjs";
import drawingImages from "./drawing-images.mjs";
import drawingLabelText from "./drawing-label-text.mjs";
import drawingNodes from "./drawing-nodes.mjs";
import drawingRedraw from "./drawing-redraw.mjs";
import drawingShapes from "./drawing-shapes.mjs";
import ElementTextureCache from "./ele-texture-cache.mjs";
import exportImage from "./export-image.mjs";
import LayeredTextureCache from "./layered-texture-cache.mjs";
import nodeShapes from "./node-shapes.mjs";
import drawingRedrawWebGL from "./webgl/drawing-redraw-webgl.mjs";

var CR = CanvasRenderer;
var CRp = CanvasRenderer.prototype;

CRp.CANVAS_LAYERS = 3;
//
CRp.SELECT_BOX = 0;
CRp.DRAG = 1;
CRp.NODE = 2;
CRp.WEBGL = 3;

CRp.CANVAS_TYPES = ["2d", "2d", "2d", "webgl2"];

CRp.BUFFER_COUNT = 3;
//
CRp.TEXTURE_BUFFER = 0;
CRp.MOTIONBLUR_BUFFER_NODE = 1;
CRp.MOTIONBLUR_BUFFER_DRAG = 2;

function CanvasRenderer(options) {
	var containerWindow = this.cy.window();
	var document = containerWindow.document;

	if (options.webgl) {
		CRp.CANVAS_LAYERS = this.CANVAS_LAYERS = 4;
		console.log("webgl rendering enabled");
	}

	this.data = {
		canvases: new Array(CRp.CANVAS_LAYERS),
		contexts: new Array(CRp.CANVAS_LAYERS),
		canvasNeedsRedraw: new Array(CRp.CANVAS_LAYERS),

		bufferCanvases: new Array(CRp.BUFFER_COUNT),
		bufferContexts: new Array(CRp.CANVAS_LAYERS),
	};

	var tapHlOffAttr = "-webkit-tap-highlight-color";
	var tapHlOffStyle = "rgba(0,0,0,0)";
	this.data.canvasContainer = document.createElement("div"); // eslint-disable-line no-undef
	var containerStyle = this.data.canvasContainer.style;
	this.data.canvasContainer.style[tapHlOffAttr] = tapHlOffStyle;
	containerStyle.position = "relative";
	containerStyle.zIndex = "0";
	containerStyle.overflow = "hidden";

	var container = options.cy.container();
	container.appendChild(this.data.canvasContainer);
	container.style[tapHlOffAttr] = tapHlOffStyle;

	var styleMap = {
		"-webkit-user-select": "none",
		"-moz-user-select": "-moz-none",
		"user-select": "none",
		"-webkit-tap-highlight-color": "rgba(0,0,0,0)",
		"outline-style": "none",
	};

	if (is.ms()) {
		styleMap["-ms-touch-action"] = "none";
		styleMap["touch-action"] = "none";
	}

	for (var i = 0; i < CRp.CANVAS_LAYERS; i++) {
		var canvas = (this.data.canvases[i] = document.createElement("canvas")); // eslint-disable-line no-undef
		var type = CRp.CANVAS_TYPES[i];
		this.data.contexts[i] = canvas.getContext(type);
		if (!this.data.contexts[i]) {
			util.error("Could not create canvas of type " + type);
		}
		Object.keys(styleMap).forEach((k) => {
			canvas.style[k] = styleMap[k];
		});
		canvas.style.position = "absolute";
		canvas.setAttribute("data-id", "layer" + i);
		canvas.style.zIndex = String(CRp.CANVAS_LAYERS - i);
		this.data.canvasContainer.appendChild(canvas);

		this.data.canvasNeedsRedraw[i] = false;
	}
	this.data.topCanvas = this.data.canvases[0];

	this.data.canvases[CRp.NODE].setAttribute(
		"data-id",
		"layer" + CRp.NODE + "-node",
	);
	this.data.canvases[CRp.SELECT_BOX].setAttribute(
		"data-id",
		"layer" + CRp.SELECT_BOX + "-selectbox",
	);
	this.data.canvases[CRp.DRAG].setAttribute(
		"data-id",
		"layer" + CRp.DRAG + "-drag",
	);
	if (this.data.canvases[CRp.WEBGL]) {
		this.data.canvases[CRp.WEBGL].setAttribute(
			"data-id",
			"layer" + CRp.WEBGL + "-webgl",
		);
	}

	for (var i = 0; i < CRp.BUFFER_COUNT; i++) {
		this.data.bufferCanvases[i] = document.createElement("canvas"); // eslint-disable-line no-undef
		this.data.bufferContexts[i] = this.data.bufferCanvases[i].getContext("2d");
		this.data.bufferCanvases[i].style.position = "absolute";
		this.data.bufferCanvases[i].setAttribute("data-id", "buffer" + i);
		this.data.bufferCanvases[i].style.zIndex = String(-i - 1);
		this.data.bufferCanvases[i].style.visibility = "hidden";
		//r.data.canvasContainer.appendChild(r.data.bufferCanvases[i]);
	}

	this.pathsEnabled = true;

	const emptyBb = makeBoundingBox();

	const getBoxCenter = (bb) => ({
		x: (bb.x1 + bb.x2) / 2,
		y: (bb.y1 + bb.y2) / 2,
	});

	const getCenterOffset = (bb) => ({ x: -bb.w / 2, y: -bb.h / 2 });

	const backgroundTimestampHasChanged = (ele) => {
		const _p = ele[0]._private;
		const same = _p.oldBackgroundTimestamp === _p.backgroundTimestamp;

		return !same;
	};

	const getStyleKey = (ele) => ele[0]._private.nodeKey;
	const getLabelKey = (ele) => ele[0]._private.labelStyleKey;
	const getSourceLabelKey = (ele) => ele[0]._private.sourceLabelStyleKey;
	const getTargetLabelKey = (ele) => ele[0]._private.targetLabelStyleKey;

	const drawElement = (context, ele, bb, scaledLabelShown, useEleOpacity) =>
		this.drawElement(context, ele, bb, false, false, useEleOpacity);
	const drawLabel = (context, ele, bb, scaledLabelShown, useEleOpacity) =>
		this.drawElementText(
			context,
			ele,
			bb,
			scaledLabelShown,
			"main",
			useEleOpacity,
		);
	const drawSourceLabel = (context, ele, bb, scaledLabelShown, useEleOpacity) =>
		this.drawElementText(
			context,
			ele,
			bb,
			scaledLabelShown,
			"source",
			useEleOpacity,
		);
	const drawTargetLabel = (context, ele, bb, scaledLabelShown, useEleOpacity) =>
		this.drawElementText(
			context,
			ele,
			bb,
			scaledLabelShown,
			"target",
			useEleOpacity,
		);

	const getElementBox = (ele) => {
		ele.boundingBox();
		return ele[0]._private.bodyBounds;
	};
	const getLabelBox = (ele) => {
		ele.boundingBox();
		return ele[0]._private.labelBounds.main || emptyBb;
	};
	const getSourceLabelBox = (ele) => {
		ele.boundingBox();
		return ele[0]._private.labelBounds.source || emptyBb;
	};
	const getTargetLabelBox = (ele) => {
		ele.boundingBox();
		return ele[0]._private.labelBounds.target || emptyBb;
	};

	const isLabelVisibleAtScale = (ele, scaledLabelShown) => scaledLabelShown;

	const getElementRotationPoint = (ele) => getBoxCenter(getElementBox(ele));

	const addTextMargin = (prefix, pt, ele) => {
		const pre = prefix ? prefix + "-" : "";

		return {
			x: pt.x + ele.pstyle(pre + "text-margin-x").pfValue,
			y: pt.y + ele.pstyle(pre + "text-margin-y").pfValue,
		};
	};

	const getRsPt = (ele, x, y) => {
		const rs = ele[0]._private.rscratch;

		return { x: rs[x], y: rs[y] };
	};

	const getLabelRotationPoint = (ele) =>
		addTextMargin("", getRsPt(ele, "labelX", "labelY"), ele);
	const getSourceLabelRotationPoint = (ele) =>
		addTextMargin("source", getRsPt(ele, "sourceLabelX", "sourceLabelY"), ele);
	const getTargetLabelRotationPoint = (ele) =>
		addTextMargin("target", getRsPt(ele, "targetLabelX", "targetLabelY"), ele);

	const getElementRotationOffset = (ele) => getCenterOffset(getElementBox(ele));
	const getSourceLabelRotationOffset = (ele) =>
		getCenterOffset(getSourceLabelBox(ele));
	const getTargetLabelRotationOffset = (ele) =>
		getCenterOffset(getTargetLabelBox(ele));

	const getLabelRotationOffset = (ele) => {
		const bb = getLabelBox(ele);
		const p = getCenterOffset(getLabelBox(ele));

		if (ele.isNode()) {
			switch (ele.pstyle("text-halign").value) {
				case "left":
					p.x = -bb.w - (bb.leftPad || 0);
					break;
				case "right":
					p.x = -(bb.rightPad || 0);
					break;
			}

			switch (ele.pstyle("text-valign").value) {
				case "top":
					p.y = -bb.h - (bb.topPad || 0);
					break;
				case "bottom":
					p.y = -(bb.botPad || 0);
					break;
			}
		}

		return p;
	};

	const eleTxrCache = (this.data.eleTxrCache = new ElementTextureCache(this, {
		getKey: getStyleKey,
		doesEleInvalidateKey: backgroundTimestampHasChanged,
		drawElement: drawElement,
		getBoundingBox: getElementBox,
		getRotationPoint: getElementRotationPoint,
		getRotationOffset: getElementRotationOffset,
		allowEdgeTxrCaching: false,
		allowParentTxrCaching: false,
	}));

	const lblTxrCache = (this.data.lblTxrCache = new ElementTextureCache(this, {
		getKey: getLabelKey,
		drawElement: drawLabel,
		getBoundingBox: getLabelBox,
		getRotationPoint: getLabelRotationPoint,
		getRotationOffset: getLabelRotationOffset,
		isVisible: isLabelVisibleAtScale,
	}));

	const slbTxrCache = (this.data.slbTxrCache = new ElementTextureCache(this, {
		getKey: getSourceLabelKey,
		drawElement: drawSourceLabel,
		getBoundingBox: getSourceLabelBox,
		getRotationPoint: getSourceLabelRotationPoint,
		getRotationOffset: getSourceLabelRotationOffset,
		isVisible: isLabelVisibleAtScale,
	}));

	const tlbTxrCache = (this.data.tlbTxrCache = new ElementTextureCache(this, {
		getKey: getTargetLabelKey,
		drawElement: drawTargetLabel,
		getBoundingBox: getTargetLabelBox,
		getRotationPoint: getTargetLabelRotationPoint,
		getRotationOffset: getTargetLabelRotationOffset,
		isVisible: isLabelVisibleAtScale,
	}));

	const lyrTxrCache = (this.data.lyrTxrCache = new LayeredTextureCache(this));

	this.onUpdateEleCalcs(function invalidateTextureCaches(willDraw, eles) {
		// each cache should check for sub-key diff to see that the update affects that cache particularly
		eleTxrCache.invalidateElements(eles);
		lblTxrCache.invalidateElements(eles);
		slbTxrCache.invalidateElements(eles);
		tlbTxrCache.invalidateElements(eles);

		// any change invalidates the layers
		lyrTxrCache.invalidateElements(eles);

		// update the old bg timestamp so diffs can be done in the ele txr caches
		for (let i = 0; i < eles.length; i++) {
			const _p = eles[i]._private;

			_p.oldBackgroundTimestamp = _p.backgroundTimestamp;
		}
	});

	const refineInLayers = (reqs) => {
		for (var i = 0; i < reqs.length; i++) {
			lyrTxrCache.enqueueElementRefinement(reqs[i].ele);
		}
	};

	eleTxrCache.onDequeue(refineInLayers);
	lblTxrCache.onDequeue(refineInLayers);
	slbTxrCache.onDequeue(refineInLayers);
	tlbTxrCache.onDequeue(refineInLayers);

	if (options.webgl) {
		this.initWebgl(options, {
			getStyleKey,
			getLabelKey,
			getSourceLabelKey,
			getTargetLabelKey,
			drawElement,
			drawLabel,
			drawSourceLabel,
			drawTargetLabel,
			getElementBox,
			getLabelBox,
			getSourceLabelBox,
			getTargetLabelBox,
			getElementRotationPoint,
			getElementRotationOffset,
			getLabelRotationPoint,
			getSourceLabelRotationPoint,
			getTargetLabelRotationPoint,
			getLabelRotationOffset,
			getSourceLabelRotationOffset,
			getTargetLabelRotationOffset,
		});
	}
}

CRp.redrawHint = function (group, bool) {
	switch (group) {
		case "eles":
			this.data.canvasNeedsRedraw[CRp.NODE] = bool;
			break;
		case "drag":
			this.data.canvasNeedsRedraw[CRp.DRAG] = bool;
			break;
		case "select":
			this.data.canvasNeedsRedraw[CRp.SELECT_BOX] = bool;
			break;
		case "gc":
			this.data.gc = true;
			break;
	}
};

// whether to use Path2D caching for drawing
var pathsImpld = typeof Path2D !== "undefined";

CRp.path2dEnabled = function (on) {
	if (on === undefined) {
		return this.pathsEnabled;
	}

	this.pathsEnabled = on ? true : false;
};

CRp.usePaths = function () {
	return pathsImpld && this.pathsEnabled;
};

CRp.setImgSmoothing = (context, bool) => {
	if (context.imageSmoothingEnabled != null) {
		context.imageSmoothingEnabled = bool;
	} else {
		context.webkitImageSmoothingEnabled = bool;
		context.mozImageSmoothingEnabled = bool;
		context.msImageSmoothingEnabled = bool;
	}
};

CRp.getImgSmoothing = (context) => {
	if (context.imageSmoothingEnabled != null) {
		return context.imageSmoothingEnabled;
	} else {
		return (
			context.webkitImageSmoothingEnabled ||
			context.mozImageSmoothingEnabled ||
			context.msImageSmoothingEnabled
		);
	}
};

CRp.makeOffscreenCanvas = function (width, height) {
	let canvas;

	if (typeof OffscreenCanvas !== typeof undefined) {
		canvas = new OffscreenCanvas(width, height);
	} else {
		var containerWindow = this.cy.window();
		var document = containerWindow.document;
		canvas = document.createElement("canvas"); // eslint-disable-line no-undef
		canvas.width = width;
		canvas.height = height;
	}

	return canvas;
};

[
	arrowShapes,
	drawingElements,
	drawingEdges,
	drawingImages,
	drawingLabelText,
	drawingNodes,
	drawingRedraw,
	drawingRedrawWebGL,
	drawingShapes,
	exportImage,
	nodeShapes,
].forEach((props) => {
	util.extend(CRp, props);
});

export default CR;
