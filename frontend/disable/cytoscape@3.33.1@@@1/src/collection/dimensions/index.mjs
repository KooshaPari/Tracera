import * as util from "../../util/index.mjs";
import bounds from "./bounds.mjs";
import edgePoints from "./edge-points.mjs";
import position from "./position.mjs";
import widthHeight from "./width-height.mjs";

export default util.assign({}, position, bounds, widthHeight, edgePoints);
