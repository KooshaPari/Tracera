Object.defineProperty(exports, "__esModule", {
	value: true,
});

exports.default = (worker, concurrency) => {
	// Start with a normal queue
	var q = (0, _queue2.default)(worker, concurrency);

	var { push, pushAsync } = q;

	q._tasks = new _Heap2.default();
	q._createTaskItem = ({ data, priority }, callback) => {
		return {
			data,
			priority,
			callback,
		};
	};

	function createDataItems(tasks, priority) {
		if (!Array.isArray(tasks)) {
			return { data: tasks, priority };
		}
		return tasks.map((data) => {
			return { data, priority };
		});
	}

	// Override push to accept second parameter representing priority
	q.push = (data, priority = 0, callback) =>
		push(createDataItems(data, priority), callback);

	q.pushAsync = (data, priority = 0, callback) =>
		pushAsync(createDataItems(data, priority), callback);

	// Remove unshift functions
	delete q.unshift;
	delete q.unshiftAsync;

	return q;
};

var _queue = require("./queue.js");

var _queue2 = _interopRequireDefault(_queue);

var _Heap = require("./internal/Heap.js");

var _Heap2 = _interopRequireDefault(_Heap);

function _interopRequireDefault(obj) {
	return obj && obj.__esModule ? obj : { default: obj };
}

module.exports = exports.default;
