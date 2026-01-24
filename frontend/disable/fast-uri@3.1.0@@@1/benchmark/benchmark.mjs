import { Bench } from "tinybench";
import {
	equal as uriJsEqual,
	parse as uriJsParse,
	resolve as uriJsResolve,
	serialize as uriJsSerialize,
} from "uri-js";
import { fastUri } from "../index.js";

const base = "uri://a/b/c/d;p?q";

const domain = "https://example.com/foo#bar$fiz";
const ipv4 = "//10.10.10.10";
const ipv6 = "//[2001:db8::7]";
const urn = "urn:foo:a123,456";
const urnuuid = "urn:uuid:f81d4fae-7dec-11d0-a765-00a0c91e6bf6";

const urnuuidComponent = {
	scheme: "urn",
	nid: "uuid",
	uuid: "f81d4fae-7dec-11d0-a765-00a0c91e6bf6",
};

const {
	parse: fastUriParse,
	serialize: fastUriSerialize,
	resolve: fastUriResolve,
	equal: fastUriEqual,
} = fastUri;

// Initialization as there is a lot to parse at first
// eg: regexes
fastUriParse(domain);
uriJsParse(domain);

const benchFastUri = new Bench({ name: "fast-uri benchmark" });
const benchUriJs = new Bench({ name: "uri-js benchmark" });
const benchWHATWG = new Bench({ name: "WHATWG URL benchmark" });

benchFastUri.add("fast-uri: parse domain", () => {
	fastUriParse(domain);
});
benchUriJs.add("urijs: parse domain", () => {
	uriJsParse(domain);
});
benchWHATWG.add("WHATWG URL: parse domain", () => {
	// eslint-disable-next-line
	new URL(domain);
});
benchFastUri.add("fast-uri: parse IPv4", () => {
	fastUriParse(ipv4);
});
benchUriJs.add("urijs: parse IPv4", () => {
	uriJsParse(ipv4);
});
benchFastUri.add("fast-uri: parse IPv6", () => {
	fastUriParse(ipv6);
});
benchUriJs.add("urijs: parse IPv6", () => {
	uriJsParse(ipv6);
});
benchFastUri.add("fast-uri: parse URN", () => {
	fastUriParse(urn);
});
benchUriJs.add("urijs: parse URN", () => {
	uriJsParse(urn);
});
benchWHATWG.add("WHATWG URL: parse URN", () => {
	// eslint-disable-next-line
	new URL(urn);
});
benchFastUri.add("fast-uri: parse URN uuid", () => {
	fastUriParse(urnuuid);
});
benchUriJs.add("urijs: parse URN uuid", () => {
	uriJsParse(urnuuid);
});
benchFastUri.add("fast-uri: serialize URN uuid", () => {
	fastUriSerialize(urnuuidComponent);
});
benchUriJs.add("uri-js: serialize URN uuid", () => {
	uriJsSerialize(urnuuidComponent);
});
benchFastUri.add("fast-uri: serialize uri", () => {
	fastUriSerialize({
		scheme: "uri",
		userinfo: "foo:bar",
		host: "example.com",
		port: 1,
		path: "path",
		query: "query",
		fragment: "fragment",
	});
});
benchUriJs.add("urijs: serialize uri", () => {
	uriJsSerialize({
		scheme: "uri",
		userinfo: "foo:bar",
		host: "example.com",
		port: 1,
		path: "path",
		query: "query",
		fragment: "fragment",
	});
});
benchFastUri.add("fast-uri: serialize long uri with dots", () => {
	fastUriSerialize({
		scheme: "uri",
		userinfo: "foo:bar",
		host: "example.com",
		port: 1,
		path: "./a/./b/c/../.././d/../e/f/.././/",
		query: "query",
		fragment: "fragment",
	});
});
benchUriJs.add("urijs: serialize long uri with dots", () => {
	uriJsSerialize({
		scheme: "uri",
		userinfo: "foo:bar",
		host: "example.com",
		port: 1,
		path: "./a/./b/c/../.././d/../e/f/.././/",
		query: "query",
		fragment: "fragment",
	});
});
benchFastUri.add("fast-uri: serialize IPv6", () => {
	fastUriSerialize({ host: "2606:2800:220:1:248:1893:25c8:1946" });
});
benchUriJs.add("urijs: serialize IPv6", () => {
	uriJsSerialize({ host: "2606:2800:220:1:248:1893:25c8:1946" });
});
benchFastUri.add("fast-uri: serialize ws", () => {
	fastUriSerialize({
		scheme: "ws",
		host: "example.com",
		resourceName: "/foo?bar",
		secure: true,
	});
});
benchUriJs.add("urijs: serialize ws", () => {
	uriJsSerialize({
		scheme: "ws",
		host: "example.com",
		resourceName: "/foo?bar",
		secure: true,
	});
});
benchFastUri.add("fast-uri: resolve", () => {
	fastUriResolve(base, "../../../g");
});
benchUriJs.add("urijs: resolve", () => {
	uriJsResolve(base, "../../../g");
});

benchFastUri.add("fast-uri: equal", () => {
	fastUriEqual(
		"example://a/b/c/%7Bfoo%7D",
		"eXAMPLE://a/./b/../b/%63/%7bfoo%7d",
	);
});
benchUriJs.add("urijs: equal", () => {
	uriJsEqual("example://a/b/c/%7Bfoo%7D", "eXAMPLE://a/./b/../b/%63/%7bfoo%7d");
});

await benchFastUri.run();
console.log(benchFastUri.name);
console.table(benchFastUri.table());

await benchUriJs.run();
console.log(benchUriJs.name);
console.table(benchUriJs.table());

await benchWHATWG.run();
console.log(benchWHATWG.name);
console.table(benchWHATWG.table());
