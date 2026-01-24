import * as is from "../../../is.mjs";
import * as util from "../../../util/index.mjs";

import arrowShapes from "./arrow-shapes.mjs";
import coordEleMath from "./coord-ele-math/index.mjs";
import images from "./images.mjs";
import loadListeners from "./load-listeners.mjs";
import nodeShapes from "./node-shapes.mjs";
import redraw from "./redraw.mjs";

var BaseRenderer = function (options) {
	this.init(options);
};
var BR = BaseRenderer;
var BRp = BR.prototype;

BRp.clientFunctions = [
	"redrawHint",
	"render",
	"renderTo",
	"matchCanvasSize",
	"nodeShapeImpl",
	"arrowShapeImpl",
];

BRp.init = function (options) {
	this.options = options;

	this.cy = options.cy;

	var ctr = (this.container = options.cy.container());
	var containerWindow = this.cy.window();

	// prepend a stylesheet in the head such that
	if (containerWindow) {
		var document = containerWindow.document;
		var head = document.head;
		var stylesheetId = "__________cytoscape_stylesheet";
		var className = "__________cytoscape_container";
		var stylesheetAlreadyExists = document.getElementById(stylesheetId) != null;

		if (ctr.className.indexOf(className) < 0) {
			ctr.className = (ctr.className || "") + " " + className;
		}

		if (!stylesheetAlreadyExists) {
			var stylesheet = document.createElement("style");

			stylesheet.id = stylesheetId;
			stylesheet.textContent = "." + className + " { position: relative; }";

			head.insertBefore(stylesheet, head.children[0]); // first so lowest priority
		}

		var computedStyle = containerWindow.getComputedStyle(ctr);
		var position = computedStyle.getPropertyValue("position");

		if (position === "static") {
			util.warn(
				"A Cytoscape container has style position:static and so can not use UI extensions properly",
			);
		}
	}

	this.selection = [undefined, undefined, undefined, undefined, 0]; // Coordinates for selection box, plus enabled flag

	this.bezierProjPcts = [0.05, 0.225, 0.4, 0.5, 0.6, 0.775, 0.95];

	//--Pointer-related data
	this.hoverData = {
		down: null,
		last: null,
		downTime: null,
		triggerMode: null,
		dragging: false,
		initialPan: [null, null],
		capture: false,
	};

	this.dragData = { possibleDragElements: [] };

	this.touchData = {
		start: null,
		capture: false,

		// These 3 fields related to tap, taphold events
		startPosition: [null, null, null, null, null, null],
		singleTouchStartTime: null,
		singleTouchMoved: true,

		now: [null, null, null, null, null, null],
		earlier: [null, null, null, null, null, null],
	};

	this.redraws = 0;
	this.showFps = options.showFps;
	this.debug = options.debug;
	this.webgl = options.webgl;

	this.hideEdgesOnViewport = options.hideEdgesOnViewport;
	this.textureOnViewport = options.textureOnViewport;
	this.wheelSensitivity = options.wheelSensitivity;
	this.motionBlurEnabled = options.motionBlur; // on by default
	this.forcedPixelRatio = is.number(options.pixelRatio)
		? options.pixelRatio
		: null;
	this.motionBlur = options.motionBlur; // for initial kick off
	this.motionBlurOpacity = options.motionBlurOpacity;
	this.motionBlurTransparency = 1 - this.motionBlurOpacity;
	this.motionBlurPxRatio = 1;
	this.mbPxRBlurry = 1; //0.8;
	this.minMbLowQualFrames = 4;
	this.fullQualityMb = false;
	this.clearedForMotionBlur = [];
	this.desktopTapThreshold = options.desktopTapThreshold;
	this.desktopTapThreshold2 =
		options.desktopTapThreshold * options.desktopTapThreshold;
	this.touchTapThreshold = options.touchTapThreshold;
	this.touchTapThreshold2 =
		options.touchTapThreshold * options.touchTapThreshold;
	this.tapholdDuration = 500;

	this.bindings = [];
	this.beforeRenderCallbacks = [];
	this.beforeRenderPriorities = {
		// higher priority execs before lower one
		animations: 400,
		eleCalcs: 300,
		eleTxrDeq: 200,
		lyrTxrDeq: 150,
		lyrTxrSkip: 100,
	};

	this.registerNodeShapes();
	this.registerArrowShapes();
	this.registerCalculationListeners();
};

BRp.notify = function (eventName, eles) {
	var cy = this.cy;

	// the renderer can't be notified after it's destroyed
	if (this.destroyed) {
		return;
	}

	if (eventName === "init") {
		this.load();
		return;
	}

	if (eventName === "destroy") {
		this.destroy();
		return;
	}

	if (
		eventName === "add" ||
		eventName === "remove" ||
		(eventName === "move" && cy.hasCompoundNodes()) ||
		eventName === "load" ||
		eventName === "zorder" ||
		eventName === "mount"
	) {
		this.invalidateCachedZSortedEles();
	}

	if (eventName === "viewport") {
		this.redrawHint("select", true);
	}

	if (eventName === "gc") {
		this.redrawHint("gc", true);
	}

	if (eventName === "load" || eventName === "resize" || eventName === "mount") {
		this.invalidateContainerClientCoordsCache();
		this.matchCanvasSize(this.container);
	}

	this.redrawHint("eles", true);
	this.redrawHint("drag", true);

	this.startRenderLoop();

	this.redraw();
};

BRp.destroy = function () {
	this.destroyed = true;

	this.cy.stopAnimationLoop();

	for (var i = 0; i < this.bindings.length; i++) {
		var binding = this.bindings[i];
		var b = binding;
		var tgt = b.target;

		(tgt.off || tgt.removeEventListener).apply(tgt, b.args);
	}

	this.bindings = [];
	this.beforeRenderCallbacks = [];
	this.onUpdateEleCalcsFns = [];

	if (this.removeObserver) {
		this.removeObserver.disconnect();
	}

	if (this.styleObserver) {
		this.styleObserver.disconnect();
	}

	if (this.resizeObserver) {
		this.resizeObserver.disconnect();
	}

	if (this.labelCalcDiv) {
		try {
			document.body.removeChild(this.labelCalcDiv); // eslint-disable-line no-undef
		} catch (e) {
			// ie10 issue #1014
		}
	}
};

BRp.isHeadless = () => false;

[arrowShapes, coordEleMath, images, loadListeners, nodeShapes, redraw].forEach(
	(props) => {
		util.extend(BRp, props);
	},
);

export default BR;
