var fs = require("fs");
var util = require("util");
var stream = require("stream");
var Readable = stream.Readable;
var Writable = stream.Writable;
var PassThrough = stream.PassThrough;
var Pend = require("pend");
var EventEmitter = require("events").EventEmitter;

exports.createFromBuffer = createFromBuffer;
exports.createFromFd = createFromFd;
exports.BufferSlicer = BufferSlicer;
exports.FdSlicer = FdSlicer;

util.inherits(FdSlicer, EventEmitter);
function FdSlicer(fd, options) {
	options = options || {};
	EventEmitter.call(this);

	this.fd = fd;
	this.pend = new Pend();
	this.pend.max = 1;
	this.refCount = 0;
	this.autoClose = !!options.autoClose;
}

FdSlicer.prototype.read = function (
	buffer,
	offset,
	length,
	position,
	callback,
) {
	this.pend.go((cb) => {
		fs.read(
			this.fd,
			buffer,
			offset,
			length,
			position,
			(err, bytesRead, buffer) => {
				cb();
				callback(err, bytesRead, buffer);
			},
		);
	});
};

FdSlicer.prototype.write = function (
	buffer,
	offset,
	length,
	position,
	callback,
) {
	this.pend.go((cb) => {
		fs.write(
			this.fd,
			buffer,
			offset,
			length,
			position,
			(err, written, buffer) => {
				cb();
				callback(err, written, buffer);
			},
		);
	});
};

FdSlicer.prototype.createReadStream = function (options) {
	return new ReadStream(this, options);
};

FdSlicer.prototype.createWriteStream = function (options) {
	return new WriteStream(this, options);
};

FdSlicer.prototype.ref = function () {
	this.refCount += 1;
};

FdSlicer.prototype.unref = function () {
	var self = this;
	self.refCount -= 1;

	if (self.refCount > 0) return;
	if (self.refCount < 0) throw new Error("invalid unref");

	if (self.autoClose) {
		fs.close(self.fd, onCloseDone);
	}

	function onCloseDone(err) {
		if (err) {
			self.emit("error", err);
		} else {
			self.emit("close");
		}
	}
};

util.inherits(ReadStream, Readable);
function ReadStream(context, options) {
	options = options || {};
	Readable.call(this, options);

	this.context = context;
	this.context.ref();

	this.start = options.start || 0;
	this.endOffset = options.end;
	this.pos = this.start;
	this.destroyed = false;
}

ReadStream.prototype._read = function (n) {
	if (this.destroyed) return;

	var toRead = Math.min(this._readableState.highWaterMark, n);
	if (this.endOffset != null) {
		toRead = Math.min(toRead, this.endOffset - this.pos);
	}
	if (toRead <= 0) {
		this.destroyed = true;
		this.push(null);
		this.context.unref();
		return;
	}
	this.context.pend.go((cb) => {
		if (this.destroyed) return cb();
		var buffer = new Buffer(toRead);
		fs.read(this.context.fd, buffer, 0, toRead, this.pos, (err, bytesRead) => {
			if (err) {
				this.destroy(err);
			} else if (bytesRead === 0) {
				this.destroyed = true;
				this.push(null);
				this.context.unref();
			} else {
				this.pos += bytesRead;
				this.push(buffer.slice(0, bytesRead));
			}
			cb();
		});
	});
};

ReadStream.prototype.destroy = function (err) {
	if (this.destroyed) return;
	err = err || new Error("stream destroyed");
	this.destroyed = true;
	this.emit("error", err);
	this.context.unref();
};

util.inherits(WriteStream, Writable);
function WriteStream(context, options) {
	options = options || {};
	Writable.call(this, options);

	this.context = context;
	this.context.ref();

	this.start = options.start || 0;
	this.endOffset = options.end == null ? Infinity : +options.end;
	this.bytesWritten = 0;
	this.pos = this.start;
	this.destroyed = false;

	this.on("finish", this.destroy.bind(this));
}

WriteStream.prototype._write = function (buffer, encoding, callback) {
	if (this.destroyed) return;

	if (this.pos + buffer.length > this.endOffset) {
		var err = new Error("maximum file length exceeded");
		err.code = "ETOOBIG";
		this.destroy();
		callback(err);
		return;
	}
	this.context.pend.go((cb) => {
		if (this.destroyed) return cb();
		fs.write(
			this.context.fd,
			buffer,
			0,
			buffer.length,
			this.pos,
			(err, bytes) => {
				if (err) {
					this.destroy();
					cb();
					callback(err);
				} else {
					this.bytesWritten += bytes;
					this.pos += bytes;
					this.emit("progress");
					cb();
					callback();
				}
			},
		);
	});
};

WriteStream.prototype.destroy = function () {
	if (this.destroyed) return;
	this.destroyed = true;
	this.context.unref();
};

util.inherits(BufferSlicer, EventEmitter);
function BufferSlicer(buffer, options) {
	EventEmitter.call(this);

	options = options || {};
	this.refCount = 0;
	this.buffer = buffer;
	this.maxChunkSize = options.maxChunkSize || Number.MAX_SAFE_INTEGER;
}

BufferSlicer.prototype.read = function (
	buffer,
	offset,
	length,
	position,
	callback,
) {
	var end = position + length;
	var delta = end - this.buffer.length;
	var written = delta > 0 ? delta : length;
	this.buffer.copy(buffer, offset, position, end);
	setImmediate(() => {
		callback(null, written);
	});
};

BufferSlicer.prototype.write = function (
	buffer,
	offset,
	length,
	position,
	callback,
) {
	buffer.copy(this.buffer, position, offset, offset + length);
	setImmediate(() => {
		callback(null, length, buffer);
	});
};

BufferSlicer.prototype.createReadStream = function (options) {
	options = options || {};
	var readStream = new PassThrough(options);
	readStream.destroyed = false;
	readStream.start = options.start || 0;
	readStream.endOffset = options.end;
	// by the time this function returns, we'll be done.
	readStream.pos = readStream.endOffset || this.buffer.length;

	// respect the maxChunkSize option to slice up the chunk into smaller pieces.
	var entireSlice = this.buffer.slice(readStream.start, readStream.pos);
	var offset = 0;
	while (true) {
		var nextOffset = offset + this.maxChunkSize;
		if (nextOffset >= entireSlice.length) {
			// last chunk
			if (offset < entireSlice.length) {
				readStream.write(entireSlice.slice(offset, entireSlice.length));
			}
			break;
		}
		readStream.write(entireSlice.slice(offset, nextOffset));
		offset = nextOffset;
	}

	readStream.end();
	readStream.destroy = () => {
		readStream.destroyed = true;
	};
	return readStream;
};

BufferSlicer.prototype.createWriteStream = function (options) {
	options = options || {};
	var writeStream = new Writable(options);
	writeStream.start = options.start || 0;
	writeStream.endOffset =
		options.end == null ? this.buffer.length : +options.end;
	writeStream.bytesWritten = 0;
	writeStream.pos = writeStream.start;
	writeStream.destroyed = false;
	writeStream._write = (buffer, encoding, callback) => {
		if (writeStream.destroyed) return;

		var end = writeStream.pos + buffer.length;
		if (end > writeStream.endOffset) {
			var err = new Error("maximum file length exceeded");
			err.code = "ETOOBIG";
			writeStream.destroyed = true;
			callback(err);
			return;
		}
		buffer.copy(this.buffer, writeStream.pos, 0, buffer.length);

		writeStream.bytesWritten += buffer.length;
		writeStream.pos = end;
		writeStream.emit("progress");
		callback();
	};
	writeStream.destroy = () => {
		writeStream.destroyed = true;
	};
	return writeStream;
};

BufferSlicer.prototype.ref = function () {
	this.refCount += 1;
};

BufferSlicer.prototype.unref = function () {
	this.refCount -= 1;

	if (this.refCount < 0) {
		throw new Error("invalid unref");
	}
};

function createFromBuffer(buffer, options) {
	return new BufferSlicer(buffer, options);
}

function createFromFd(fd, options) {
	return new FdSlicer(fd, options);
}
