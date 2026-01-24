var http = require("http");
var httpShutdown = require("./index").extend();
var should = require("chai").should();
var request = require("request");

describe("http-shutdown", (done) => {
	it("Should shutdown with no traffic", (done) => {
		var server = http
			.createServer((req, res) => {
				done.fail();
			})
			.withShutdown();

		server.listen(16789, () => {
			server.shutdown((err) => {
				should.not.exist(err);
				done();
			});
		});
	});

	it("Should shutdown with outstanding traffic", (done) => {
		var server = http
			.createServer((req, res) => {
				setTimeout(() => {
					res.writeHead(200);
					res.end("All done");
				}, 500);
			})
			.withShutdown();

		server.listen(16789, (err) => {
			request.get("http://localhost:16789/", (err, response) => {
				should.not.exist(err);
				response.statusCode.should.equal(200);
				done();
			});

			setTimeout(server.shutdown, 100);
		});
	});

	it("Should force shutdown without waiting for outstanding traffic", (done) => {
		var server = http
			.createServer((req, res) => {
				setTimeout(() => {
					done.fail();
				}, 500);
			})
			.withShutdown();

		server.listen(16789, (err) => {
			request.get("http://localhost:16789/", (err, response) => {
				should.exist(err);
				done();
			});

			setTimeout(server.forceShutdown, 100);
		});
	});
});
