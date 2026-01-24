var http = require("http");
var https = require("https");

/**
 * Expose `addShutdown`.
 */
exports = module.exports = addShutdown;

/**
 * Adds shutdown functionaility to the `http.Server` object
 * @param {http.Server} server The server to add shutdown functionaility to
 */
function addShutdown(server) {
	var connections = {};
	var isShuttingDown = false;
	var connectionCounter = 0;

	function destroy(socket, force) {
		if (force || (socket._isIdle && isShuttingDown)) {
			socket.destroy();
			delete connections[socket._connectionId];
		}
	}

	function onConnection(socket) {
		var id = connectionCounter++;
		socket._isIdle = true;
		socket._connectionId = id;
		connections[id] = socket;

		socket.on("close", () => {
			delete connections[id];
		});
	}

	server.on("request", (req, res) => {
		req.socket._isIdle = false;

		res.on("finish", () => {
			req.socket._isIdle = true;
			destroy(req.socket);
		});
	});

	server.on("connection", onConnection);
	server.on("secureConnection", onConnection);

	function shutdown(force, cb) {
		isShuttingDown = true;
		server.close((err) => {
			if (cb) {
				process.nextTick(() => {
					cb(err);
				});
			}
		});

		Object.keys(connections).forEach((key) => {
			destroy(connections[key], force);
		});
	}

	server.shutdown = (cb) => {
		shutdown(false, cb);
	};

	server.forceShutdown = (cb) => {
		shutdown(true, cb);
	};

	return server;
}

/**
 * Extends the {http.Server} object with shutdown functionaility.
 * @return {http.Server} The decorated server object
 */
exports.extend = () => {
	http.Server.prototype.withShutdown = function () {
		return addShutdown(this);
	};

	https.Server.prototype.withShutdown = function () {
		return addShutdown(this);
	};
};
