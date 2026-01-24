var assert = require("@sinonjs/referee-sinon").assert;
var calledInOrder = require("./called-in-order");
var sinon = require("@sinonjs/referee-sinon").sinon;

var testObject1 = {
	someFunction: () => {
		return;
	},
};
var testObject2 = {
	otherFunction: () => {
		return;
	},
};
var testObject3 = {
	thirdFunction: () => {
		return;
	},
};

function testMethod() {
	testObject1.someFunction();
	testObject2.otherFunction();
	testObject2.otherFunction();
	testObject2.otherFunction();
	testObject3.thirdFunction();
}

describe("calledInOrder", () => {
	beforeEach(() => {
		sinon.stub(testObject1, "someFunction");
		sinon.stub(testObject2, "otherFunction");
		sinon.stub(testObject3, "thirdFunction");
		testMethod();
	});
	afterEach(() => {
		testObject1.someFunction.restore();
		testObject2.otherFunction.restore();
		testObject3.thirdFunction.restore();
	});

	describe("given single array argument", () => {
		describe("when stubs were called in expected order", () => {
			it("returns true", () => {
				assert.isTrue(
					calledInOrder([testObject1.someFunction, testObject2.otherFunction]),
				);
				assert.isTrue(
					calledInOrder([
						testObject1.someFunction,
						testObject2.otherFunction,
						testObject2.otherFunction,
						testObject3.thirdFunction,
					]),
				);
			});
		});

		describe("when stubs were called in unexpected order", () => {
			it("returns false", () => {
				assert.isFalse(
					calledInOrder([testObject2.otherFunction, testObject1.someFunction]),
				);
				assert.isFalse(
					calledInOrder([
						testObject2.otherFunction,
						testObject1.someFunction,
						testObject1.someFunction,
						testObject3.thirdFunction,
					]),
				);
			});
		});
	});

	describe("given multiple arguments", () => {
		describe("when stubs were called in expected order", () => {
			it("returns true", () => {
				assert.isTrue(
					calledInOrder(testObject1.someFunction, testObject2.otherFunction),
				);
				assert.isTrue(
					calledInOrder(
						testObject1.someFunction,
						testObject2.otherFunction,
						testObject3.thirdFunction,
					),
				);
			});
		});

		describe("when stubs were called in unexpected order", () => {
			it("returns false", () => {
				assert.isFalse(
					calledInOrder(testObject2.otherFunction, testObject1.someFunction),
				);
				assert.isFalse(
					calledInOrder(
						testObject2.otherFunction,
						testObject1.someFunction,
						testObject3.thirdFunction,
					),
				);
			});
		});
	});
});
