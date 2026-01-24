import state from "state-local";
import {
	objectWithoutProperties as _objectWithoutProperties,
	slicedToArray as _slicedToArray,
} from "../_virtual/_rollupPluginBabelHelpers.js";
import config$1 from "../config/index.js";
import compose from "../utils/compose.js";
import merge from "../utils/deepMerge.js";
import makeCancelable from "../utils/makeCancelable.js";
import validators from "../validators/index.js";

var _excluded = ["monaco"];

/** the local state of the module */
var _state$create = state.create({
		config: config$1,
		isInitialized: false,
		resolve: null,
		reject: null,
		monaco: null,
	}),
	_state$create2 = _slicedToArray(_state$create, 2),
	getState = _state$create2[0],
	setState = _state$create2[1];

/**
 * set the loader configuration
 * @param {Object} config - the configuration object
 */
function config(globalConfig) {
	var _validators$config = validators.config(globalConfig),
		monaco = _validators$config.monaco,
		config = _objectWithoutProperties(_validators$config, _excluded);
	setState((state) => ({
		config: merge(state.config, config),
		monaco: monaco,
	}));
}

/**
 * handles the initialization of the monaco-editor
 * @return {Promise} - returns an instance of monaco (with a cancelable promise)
 */
function init() {
	var state = getState((_ref) => {
		var monaco = _ref.monaco,
			isInitialized = _ref.isInitialized,
			resolve = _ref.resolve;
		return {
			monaco: monaco,
			isInitialized: isInitialized,
			resolve: resolve,
		};
	});
	if (!state.isInitialized) {
		setState({
			isInitialized: true,
		});
		if (state.monaco) {
			state.resolve(state.monaco);
			return makeCancelable(wrapperPromise);
		}
		if (window.monaco && window.monaco.editor) {
			storeMonacoInstance(window.monaco);
			state.resolve(window.monaco);
			return makeCancelable(wrapperPromise);
		}
		compose(injectScripts, getMonacoLoaderScript)(configureLoader);
	}
	return makeCancelable(wrapperPromise);
}

/**
 * injects provided scripts into the document.body
 * @param {Object} script - an HTML script element
 * @return {Object} - the injected HTML script element
 */
function injectScripts(script) {
	return document.body.appendChild(script);
}

/**
 * creates an HTML script element with/without provided src
 * @param {string} [src] - the source path of the script
 * @return {Object} - the created HTML script element
 */
function createScript(src) {
	var script = document.createElement("script");
	return src && (script.src = src), script;
}

/**
 * creates an HTML script element with the monaco loader src
 * @return {Object} - the created HTML script element
 */
function getMonacoLoaderScript(configureLoader) {
	var state = getState((_ref2) => {
		var config = _ref2.config,
			reject = _ref2.reject;
		return {
			config: config,
			reject: reject,
		};
	});
	var loaderScript = createScript(
		"".concat(state.config.paths.vs, "/loader.js"),
	);
	loaderScript.onload = () => configureLoader();
	loaderScript.onerror = state.reject;
	return loaderScript;
}

/**
 * configures the monaco loader
 */
function configureLoader() {
	var state = getState((_ref3) => {
		var config = _ref3.config,
			resolve = _ref3.resolve,
			reject = _ref3.reject;
		return {
			config: config,
			resolve: resolve,
			reject: reject,
		};
	});
	var require = window.require;
	require.config(state.config);
	require(["vs/editor/editor.main"], (loaded) => {
		var monaco =
			loaded.m /* for 0.53 & 0.54 */ || loaded /* for other versions */;
		storeMonacoInstance(monaco);
		state.resolve(monaco);
	}, (error) => {
		state.reject(error);
	});
}

/**
 * store monaco instance in local state
 */
function storeMonacoInstance(monaco) {
	if (!getState().monaco) {
		setState({
			monaco: monaco,
		});
	}
}

/**
 * internal helper function
 * extracts stored monaco instance
 * @return {Object|null} - the monaco instance
 */
function __getMonacoInstance() {
	return getState((_ref4) => {
		var monaco = _ref4.monaco;
		return monaco;
	});
}
var wrapperPromise = new Promise((resolve, reject) =>
	setState({
		resolve: resolve,
		reject: reject,
	}),
);
var loader = {
	config: config,
	init: init,
	__getMonacoInstance: __getMonacoInstance,
};

export { loader as default };
