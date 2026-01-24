import fs from "fs";
import { Environment, napi } from "napi-wasm";
import Path from "path";
import { createWrapper } from "./wrapper.js";

let env;
const encoder = new TextEncoder();

const constants = {
	O_ACCMODE: 0o00000003,
	O_RDONLY: 0,
	O_WRONLY: 0o00000001,
	O_RDWR: 0o00000002,
	O_CREAT: 0o00000100,
	O_EXCL: 0o00000200,
	O_NOCTTY: 0o00000400,
	O_TRUNC: 0o00001000,
	O_APPEND: 0o00002000,
	O_NONBLOCK: 0o00004000,
	O_SYNC: 0o00010000,
	FASYNC: 0o00020000,
	O_DIRECT: 0o00040000,
	O_LARGEFILE: 0o00100000,
	O_DIRECTORY: 0o00200000,
	O_NOFOLLOW: 0o00400000,
	O_NOATIME: 0o01000000,
	O_CLOEXEC: 0o02000000,
};

napi.napi_get_last_error_info = () => {};

const fds = new Map();
const dirs = new Map();
const regexCache = new Map();
const watches = [null];

const wasm_env = {
	__syscall_newfstatat(dirfd, path, buf, flags) {
		const dir = dirfd === -100 ? process.cwd() : fds.get(dirfd).path;
		const p = Path.resolve(dir, env.getString(path));
		const nofollow = flags & 256;
		try {
			const stat = nofollow
				? fs.lstatSync(p, { bigint: true })
				: fs.statSync(p, { bigint: true });
			return writeStat(stat, buf);
		} catch (err) {
			env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
			return -1;
		}
	},
	__syscall_lstat64(path, buf) {
		const p = env.getString(path);
		try {
			const stat = fs.lstatSync(p, { bigint: true });
			return writeStat(stat, buf);
		} catch (err) {
			env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
			return -1;
		}
	},
	__syscall_fstat64(fd, buf) {
		try {
			const stat = fs.fstatSync(fd, { bigint: true });
			return writeStat(stat, buf);
		} catch (err) {
			env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
			return -1;
		}
	},
	__syscall_stat64(path, buf) {
		const p = env.getString(path);
		try {
			const stat = fs.statSync(p, { bigint: true });
			return writeStat(stat, buf);
		} catch (err) {
			env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
			return -1;
		}
	},
	__syscall_getdents64(fd, dirp, count) {
		const p = fds.get(fd).path;
		const dir = dirs.get(fd);
		let entries = dir?.entries;
		if (!entries) {
			try {
				entries = fs.readdirSync(p, { withFileTypes: true });
			} catch (err) {
				env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
				return -1;
			}
		}

		const start = dirp;
		let i = dir?.index || 0;
		for (; i < entries.length; i++) {
			const entry = entries[i];
			const type = entry.isFIFO()
				? 1
				: entry.isCharacterDevice()
					? 2
					: entry.isDirectory()
						? 4
						: entry.isBlockDevice()
							? 6
							: entry.isFile()
								? 8
								: entry.isSymbolicLink()
									? 10
									: entry.isSocket()
										? 12
										: 0;
			const len = align(utf8Length(entry.name) + 20, 8);
			if (dirp - start + len > count) {
				break;
			}

			// Write a linux_dirent64 struct into wasm memory.
			env.u64[dirp >> 3] = 1n; // ino
			env.u64[(dirp + 8) >> 3] = BigInt(dirp - start + len); // offset
			env.u16[(dirp + 16) >> 1] = len;
			env.memory[dirp + 18] = type;
			const { written } = encoder.encodeInto(
				entry.name,
				env.memory.subarray(dirp + 19),
			);
			env.memory[dirp + 19 + written] = 0; // null terminate
			dirp += len;
		}

		dirs.set(fd, { index: i, entries });
		return dirp - start;
	},
	__syscall_openat(dirfd, path, flags, mode) {
		// Convert flags to Node values.
		let f = 0;
		for (const c in constants) {
			if (flags & constants[c]) {
				f |= fs.constants[c] || 0;
			}
		}
		const dir = dirfd === -100 ? process.cwd() : fds.get(dirfd)?.path;
		if (!dir) {
			env.i32[env.instance.exports.__errno_location >> 2] = 9970; // ENOTDIR
			return -1;
		}
		const p = Path.resolve(dir, env.getString(path));
		try {
			const fd = fs.openSync(p, f);
			fds.set(fd, { path: p, flags });
			return fd;
		} catch (err) {
			env.i32[env.instance.exports.__errno_location >> 2] = err.errno;
			return -1;
		}
	},
	__syscall_fcntl64(fd, cmd) {
		switch (cmd) {
			case 3:
				return fds.get(fd).flags;
			case 2:
				return 0;
			default:
				throw new Error("Unknown fcntl64 call: " + cmd);
		}
	},
	__syscall_ioctl() {},
	emscripten_resize_heap() {
		return 0;
	},
	_abort_js() {},
	wasm_backend_add_watch(filename, backend) {
		const path = env.getString(filename);
		const watch = fs.watch(
			path,
			{ encoding: "buffer" },
			(eventType, filename) => {
				if (filename) {
					const type = eventType === "change" ? 1 : 2;
					const fptr = env.instance.exports.malloc(filename.byteLength + 1);
					env.memory.set(filename, fptr);
					env.memory[fptr + filename.byteLength] = 0;
					env.instance.exports.wasm_backend_event_handler(
						backend,
						wd,
						type,
						fptr,
					);
					env.instance.exports.free(fptr);
				}
			},
		);

		const wd = watches.length;
		watches.push(watch);
		return wd;
	},
	wasm_backend_remove_watch(wd) {
		watches[wd].close();
		watches[wd] = undefined;
	},
	set_timeout(ms, ctx) {
		return setTimeout(() => {
			env.instance.exports.on_timeout(ctx);
		}, ms);
	},
	clear_timeout(t) {
		clearTimeout(t);
	},
	_setitimer_js() {},
	emscripten_date_now() {
		return Date.now();
	},
	_emscripten_get_now_is_monotonic() {
		return true;
	},
	_emscripten_runtime_keepalive_clear() {},
	emscripten_get_now() {
		return performance.now();
	},
	wasm_regex_match(string, regex) {
		let re = regexCache.get(regex);
		if (!re) {
			re = new RegExp(env.getString(regex));
			regexCache.set(regex, re);
		}
		return re.test(env.getString(string)) ? 1 : 0;
	},
};

const wasi = {
	fd_close(fd) {
		fs.closeSync(fd);
		fds.delete(fd);
		dirs.delete(fd);
		return 0;
	},
	fd_seek(fd, offset_low, offset_high, whence, newOffset) {
		return 0;
	},
	fd_write(fd, iov, iovcnt, pnum) {
		const buffers = [];
		for (let i = 0; i < iovcnt; i++) {
			const ptr = env.u32[iov >> 2];
			const len = env.u32[(iov + 4) >> 2];
			iov += 8;
			if (len > 0) {
				buffers.push(env.memory.subarray(ptr, ptr + len));
			}
		}
		const wrote = fs.writevSync(fd, buffers);
		env.u32[pnum >> 2] = wrote;
		return 0;
	},
	fd_read(fd, iov, iovcnt, pnum) {
		const buffers = [];
		for (let i = 0; i < iovcnt; i++) {
			const ptr = env.u32[iov >> 2];
			const len = env.u32[(iov + 4) >> 2];
			iov += 8;
			if (len > 0) {
				buffers.push(env.memory.subarray(ptr, ptr + len));
			}
		}

		const read = fs.readvSync(fd, buffers);
		env.u32[pnum >> 2] = read;
		return 0;
	},
	proc_exit() {},
	clock_time_get() {},
};

function writeStat(stat, buf) {
	env.i32[buf >> 2] = Number(stat.dev);
	env.i32[(buf + 4) >> 2] = Number(stat.mode);
	env.u32[(buf + 8) >> 2] = Number(stat.nlink);
	env.i32[(buf + 12) >> 2] = Number(stat.uid);
	env.i32[(buf + 16) >> 2] = Number(stat.gid);
	env.i32[(buf + 20) >> 2] = Number(stat.rdev);
	env.u64[(buf + 24) >> 3] = stat.size;
	env.i32[(buf + 32) >> 2] = Number(stat.blksize);
	env.i32[(buf + 36) >> 2] = Number(stat.blocks);
	env.u64[(buf + 40) >> 3] = stat.atimeMs;
	env.u32[(buf + 48) >> 2] = Number(stat.atimeNs);
	env.u64[(buf + 56) >> 3] = stat.mtimeMs;
	env.u32[(buf + 64) >> 2] = Number(stat.mtimeNs);
	env.u64[(buf + 72) >> 3] = stat.ctimeMs;
	env.u32[(buf + 80) >> 2] = Number(stat.ctimeNs);
	env.u64[(buf + 88) >> 3] = stat.ino;
	return 0;
}

function utf8Length(string) {
	let len = 0;
	for (let i = 0; i < string.length; i++) {
		let c = string.charCodeAt(i);

		if (c >= 0xd800 && c <= 0xdbff && i < string.length - 1) {
			const c2 = string.charCodeAt(++i);
			if ((c2 & 0xfc00) === 0xdc00) {
				c = ((c & 0x3ff) << 10) + (c2 & 0x3ff) + 0x10000;
			} else {
				// unmatched surrogate.
				i--;
			}
		}

		if ((c & 0xffffff80) === 0) {
			len++;
		} else if ((c & 0xfffff800) === 0) {
			len += 2;
		} else if ((c & 0xffff0000) === 0) {
			len += 3;
		} else if ((c & 0xffe00000) === 0) {
			len += 4;
		}
	}
	return len;
}

function align(len, p) {
	return Math.ceil(len / p) * p;
}

const wasmBytes = fs.readFileSync(new URL("watcher.wasm", import.meta.url));
const wasmModule = new WebAssembly.Module(wasmBytes);
const instance = new WebAssembly.Instance(wasmModule, {
	napi,
	env: wasm_env,
	wasi_snapshot_preview1: wasi,
});

env = new Environment(instance);
const wrapper = createWrapper(env.exports);

export function writeSnapshot(dir, snapshot, opts) {
	return wrapper.writeSnapshot(dir, snapshot, opts);
}

export function getEventsSince(dir, snapshot, opts) {
	return wrapper.getEventsSince(dir, snapshot, opts);
}

export function subscribe(dir, fn, opts) {
	return wrapper.subscribe(dir, fn, opts);
}

export function unsubscribe(dir, fn, opts) {
	return wrapper.unsubscribe(dir, fn, opts);
}
