// Mock ELK for tests to avoid worker initialization issues
export class ELK {
  async layout() {
    return {
      children: [],
      edges: [],
      height: 0,
      id: 'root',
      width: 0,
      x: 0,
      y: 0,
    };
  }
}

export default ELK;
