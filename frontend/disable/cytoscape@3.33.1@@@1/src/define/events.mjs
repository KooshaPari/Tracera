import Promise from "../promise.mjs";

const define = {
	eventAliasesOn: (proto) => {
		const p = proto;

		p.addListener = p.listen = p.bind = p.on;
		p.unlisten = p.unbind = p.off = p.removeListener;
		p.trigger = p.emit;

		// this is just a wrapper alias of .on()
		p.pon = p.promiseOn = function (events, selector) {
			const args = Array.prototype.slice.call(arguments, 0);

			return new Promise((resolve, reject) => {
				const callback = (e) => {
					this.off.apply(this, offArgs);

					resolve(e);
				};

				const onArgs = args.concat([callback]);
				const offArgs = onArgs.concat([]);

				this.on.apply(this, onArgs);
			});
		};
	},
}; // define

export default define;
