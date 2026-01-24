"use strict";
// `CreateIterResultObject` abstract operation
// https://tc39.es/ecma262/#sec-createiterresultobject
module.exports = (value, done) => ({ value: value, done: done });
