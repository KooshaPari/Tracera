"use strict";
require("../../modules/es.json.to-string-tag");
require("../../modules/es.math.to-string-tag");
require("../../modules/es.object.to-string");
require("../../modules/es.reflect.to-string-tag");
var classof = require("../../internals/classof");

module.exports = (it) => "[object " + classof(it) + "]";
