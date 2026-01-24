type AsyncTuple<ErrorType = Error, DataType = unknown> =
	| {
			error: ErrorType;
			data: null;
	  }
	| {
			error: null;
			data: DataType;
	  };
/**
 * Gracefully handles a given Promise factory.
 * @example
 * const { error, data } = await until(() => asyncAction())
 */
declare const until: <ErrorType = Error, DataType = unknown>(
	promise: () => Promise<DataType>,
) => Promise<AsyncTuple<ErrorType, DataType>>;

export { until };
