"use strict";
var store = require("../internals/shared-store");

module.exports = (key, value) => store[key] || (store[key] = value || {});
