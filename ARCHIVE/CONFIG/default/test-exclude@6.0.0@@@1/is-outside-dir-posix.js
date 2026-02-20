'use strict';

const path = require('path');

module.exports = function(dir, filename) {
    return path.relative(dir, filename).startsWith('..');
};
