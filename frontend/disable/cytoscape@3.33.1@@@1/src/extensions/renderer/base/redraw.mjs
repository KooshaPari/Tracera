import * as util from "../../../util/index.mjs";

var BRp = {};

BRp.timeToRender = function () {
	return this.redrawTotalTime / this.redrawCount;
};

BRp.redraw = function (options) {
	options = options || util.staticEmptyObject();

	if (this.averageRedrawTime === undefined) {
		this.averageRedrawTime = 0;
	}
	if (this.lastRedrawTime === undefined) {
		this.lastRedrawTime = 0;
	}
	if (this.lastDrawTime === undefined) {
		this.lastDrawTime = 0;
	}

	this.requestedFrame = true;
	this.renderOptions = options;
};

BRp.beforeRender = function (fn, priority) {
	// the renderer can't add tick callbacks when destroyed
	if (this.destroyed) {
		return;
	}

	if (priority == null) {
		util.error("Priority is not optional for beforeRender");
	}

	var cbs = this.beforeRenderCallbacks;

	cbs.push({ fn: fn, priority: priority });

	// higher priority callbacks executed first
	cbs.sort((a, b) => b.priority - a.priority);
};

var beforeRenderCallbacks = (r, willDraw, startTime) => {
	var cbs = r.beforeRenderCallbacks;

	for (var i = 0; i < cbs.length; i++) {
		cbs[i].fn(willDraw, startTime);
	}
};

BRp.startRenderLoop = function () {
	var cy = this.cy;

	if (this.renderLoopStarted) {
		return;
	} else {
		this.renderLoopStarted = true;
	}

	var renderFn = (requestTime) => {
		if (this.destroyed) {
			return;
		}

		if (cy.batching()) {
			// mid-batch, none of these should run
			// - pre frame hooks (calculations, texture caches, style, etc.)
			// - any drawing
		} else if (this.requestedFrame && !this.skipFrame) {
			beforeRenderCallbacks(this, true, requestTime);

			var startTime = util.performanceNow();

			this.render(this.renderOptions);

			var endTime = (this.lastDrawTime = util.performanceNow());

			if (this.averageRedrawTime === undefined) {
				this.averageRedrawTime = endTime - startTime;
			}

			if (this.redrawCount === undefined) {
				this.redrawCount = 0;
			}

			this.redrawCount++;

			if (this.redrawTotalTime === undefined) {
				this.redrawTotalTime = 0;
			}

			var duration = endTime - startTime;

			this.redrawTotalTime += duration;
			this.lastRedrawTime = duration;

			// use a weighted average with a bias from the previous average so we don't spike so easily
			this.averageRedrawTime = this.averageRedrawTime / 2 + duration / 2;

			this.requestedFrame = false;
		} else {
			beforeRenderCallbacks(this, false, requestTime);
		}

		this.skipFrame = false;

		util.requestAnimationFrame(renderFn);
	};

	util.requestAnimationFrame(renderFn);
};

export default BRp;
