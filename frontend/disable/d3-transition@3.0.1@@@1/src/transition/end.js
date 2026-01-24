import { set } from "./schedule.js";

export default function () {
	var on0,
		on1,
		id = this._id,
		size = this.size();
	return new Promise((resolve, reject) => {
		var cancel = { value: reject },
			end = {
				value: () => {
					if (--size === 0) resolve();
				},
			};

		this.each(function () {
			var schedule = set(this, id),
				on = schedule.on;

			// If this node shared a dispatch with the previous node,
			// just assign the updated shared dispatch and we’re done!
			// Otherwise, copy-on-write.
			if (on !== on0) {
				on1 = (on0 = on).copy();
				on1._.cancel.push(cancel);
				on1._.interrupt.push(cancel);
				on1._.end.push(end);
			}

			schedule.on = on1;
		});

		// The selection was empty, resolve end immediately
		if (size === 0) resolve();
	});
}
