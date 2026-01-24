var async = require("./async.js");

// API
module.exports = {
	iterator: wrapIterator,
	callback: wrapCallback,
};

/**
 * Wraps iterators with long signature
 *
 * @this    ReadableAsyncKit#
 * @param   {function} iterator - function to wrap
 * @returns {function} - wrapped function
 */
function wrapIterator(iterator) {
	return (item, key, cb) => {
		var aborter,
			wrappedCb = async(wrapIteratorCallback.call(this, cb, key));

		this.jobs[key] = wrappedCb;

		// it's either shortcut (item, cb)
		if (iterator.length == 2) {
			aborter = iterator(item, wrappedCb);
		}
		// or long format (item, key, cb)
		else {
			aborter = iterator(item, key, wrappedCb);
		}

		return aborter;
	};
}

/**
 * Wraps provided callback function
 * allowing to execute snitch function before
 * real callback
 *
 * @this    ReadableAsyncKit#
 * @param   {function} callback - function to wrap
 * @returns {function} - wrapped function
 */
function wrapCallback(callback) {
	var wrapped = (error, result) => finisher.call(this, error, result, callback);

	return wrapped;
}

/**
 * Wraps provided iterator callback function
 * makes sure snitch only called once,
 * but passes secondary calls to the original callback
 *
 * @this    ReadableAsyncKit#
 * @param   {function} callback - callback to wrap
 * @param   {number|string} key - iteration key
 * @returns {function} wrapped callback
 */
function wrapIteratorCallback(callback, key) {
	return (error, output) => {
		// don't repeat yourself
		if (!(key in this.jobs)) {
			callback(error, output);
			return;
		}

		// clean up jobs
		delete this.jobs[key];

		return streamer.call(this, error, { key: key, value: output }, callback);
	};
}

/**
 * Stream wrapper for iterator callback
 *
 * @this  ReadableAsyncKit#
 * @param {mixed} error - error response
 * @param {mixed} output - iterator output
 * @param {function} callback - callback that expects iterator results
 */
function streamer(error, output, callback) {
	if (error && !this.error) {
		this.error = error;
		this.pause();
		this.emit("error", error);
		// send back value only, as expected
		callback(error, output && output.value);
		return;
	}

	// stream stuff
	this.push(output);

	// back to original track
	// send back value only, as expected
	callback(error, output && output.value);
}

/**
 * Stream wrapper for finishing callback
 *
 * @this  ReadableAsyncKit#
 * @param {mixed} error - error response
 * @param {mixed} output - iterator output
 * @param {function} callback - callback that expects final results
 */
function finisher(error, output, callback) {
	// signal end of the stream
	// only for successfully finished streams
	if (!error) {
		this.push(null);
	}

	// back to original track
	callback(error, output);
}
