// Mock ELK for tests to avoid worker initialization issues
export class ELK {
	layout() {
		return Promise.resolve({
			id: "root",
			children: [],
			edges: [],
			x: 0,
			y: 0,
			width: 0,
			height: 0,
		});
	}
}

export default ELK;
