export const DEFAULT_HASH_SEED = 9261;
const K = 65599; // 37 also works pretty well
export const DEFAULT_HASH_SEED_ALT = 5381;

export const hashIterableInts = (iterator, seed = DEFAULT_HASH_SEED) => {
	// sdbm/string-hash
	let hash = seed;
	let entry;

	for (;;) {
		entry = iterator.next();

		if (entry.done) {
			break;
		}

		hash = (hash * K + entry.value) | 0;
	}

	return hash;
};

export const hashInt = (num, seed = DEFAULT_HASH_SEED) => {
	// sdbm/string-hash
	return (seed * K + num) | 0;
};

export const hashIntAlt = (num, seed = DEFAULT_HASH_SEED_ALT) => {
	// djb2/string-hash
	return ((seed << 5) + seed + num) | 0;
};

export const combineHashes = (hash1, hash2) => hash1 * 0x200000 + hash2;

export const combineHashesArray = (hashes) => hashes[0] * 0x200000 + hashes[1];

export const hashArrays = (hashes1, hashes2) => [
	hashInt(hashes1[0], hashes2[0]),
	hashIntAlt(hashes1[1], hashes2[1]),
];

export const hashIntsArray = (ints, seed) => {
	const entry = { value: 0, done: false };
	let i = 0;
	const length = ints.length;

	const iterator = {
		next() {
			if (i < length) {
				entry.value = ints[i++];
			} else {
				entry.done = true;
			}

			return entry;
		},
	};

	return hashIterableInts(iterator, seed);
};

export const hashString = (str, seed) => {
	const entry = { value: 0, done: false };
	let i = 0;
	const length = str.length;

	const iterator = {
		next() {
			if (i < length) {
				entry.value = str.charCodeAt(i++);
			} else {
				entry.done = true;
			}

			return entry;
		},
	};

	return hashIterableInts(iterator, seed);
};

export const hashStrings = function () {
	return hashStringsArray(arguments);
};

export const hashStringsArray = (strs) => {
	let hash;

	for (let i = 0; i < strs.length; i++) {
		const str = strs[i];

		if (i === 0) {
			hash = hashString(str);
		} else {
			hash = hashString(str, hash);
		}
	}

	return hash;
};
