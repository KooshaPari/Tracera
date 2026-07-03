// Ambient declaration for the `three` package used by electrobun's internal
// WebGPU adapter. This is required because electrobun's dist/api/bun/index.ts
// imports from "three" and skipLibCheck only covers .d.ts files, not .ts
// source files resolved via package imports.
declare module "three" {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const any: any;
  export = any;
}
