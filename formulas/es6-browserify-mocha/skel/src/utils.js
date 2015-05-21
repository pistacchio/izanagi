require("babel/polyfill");

const _ = require('lodash');

_.each(_.keys(_), k => (global || window)[k === 'isNaN' ? '_isNaN' : k] = _[k]);


const flattenFunctions = obj => {
    if (isFunction(obj)) return obj.toString().replace(/[\s\t]/gi, '');
    if (isArray(obj)) return map(obj, flattenFunctions);
    if (isObject(obj)) return mapValues(obj, flattenFunctions);

    return obj;
};

const superEqual = (x1, x2) => {
    return isEqual(flattenFunctions(x1), flattenFunctions(x2));
};

(global || window).superEqual       = superEqual;
(global || window).flattenFunctions = flattenFunctions;