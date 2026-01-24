const internals = {};

module.exports = (promise) => !!promise && typeof promise.then === "function";
