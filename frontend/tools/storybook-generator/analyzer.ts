/**
 * Component Analyzer for TraceRTM Storybook Generator
 * Extracts component props, variants, and metadata using TypeScript AST
 */

import type { SourceFile } from 'ts-morph';

import { Project, SyntaxKind } from 'ts-morph';

import type { PropInfo, VariantInfo } from './config';

export interface ComponentInfo {
  name: string;
  filePath: string;
  exportType: 'default' | 'named';
  variants: VariantInfo[];
  props: PropInfo[];
  hasCVA: boolean;
}

/**
 * Analyze a component file and extract metadata
 */
export function analyzeComponent(filePath: string): ComponentInfo | null {
  const project = new Project({
    compilerOptions: {
      jsx: 2, // React JSX
      target: 99, // ESNext
    },
  });

  const sourceFile = project.addSourceFileAtPath(filePath);
  const componentName = extractComponentName(sourceFile);

  if (!componentName) {
    return null;
  }

  const variants = extractCVAVariants(sourceFile);
  const props = extractComponentProps(sourceFile, componentName);
  const hasCVA = variants.length > 0;
  const exportType = getExportType(sourceFile, componentName);

  return {
    exportType,
    filePath,
    hasCVA,
    name: componentName,
    props,
    variants,
  };
}

/**
 * Extract component name from file
 */
function extractComponentName(sourceFile: SourceFile): string | null {
  // Look for exported components (forwardRef or regular function)
  const exportAssignments = sourceFile.getDescendantsOfKind(SyntaxKind.VariableDeclaration);

  for (const decl of exportAssignments) {
    const initializer = decl.getInitializer();
    if (!initializer) {
      continue;
    }

    // Check for forwardRef pattern
    if (initializer.getText().includes('forwardRef')) {
      return decl.getName();
    }

    // Check for function component pattern
    if (
      initializer.getKind() === SyntaxKind.ArrowFunction ||
      initializer.getKind() === SyntaxKind.FunctionExpression
    ) {
      // Check if it returns JSX
      const returnStatements = initializer.getDescendantsOfKind(SyntaxKind.ReturnStatement);
      for (const ret of returnStatements) {
        const expr = ret.getExpression();
        if (
          expr &&
          (expr.getKind() === SyntaxKind.JsxElement ||
            expr.getKind() === SyntaxKind.JsxSelfClosingElement)
        ) {
          return decl.getName();
        }
      }
    }
  }

  // Look for default export
  const defaultExport = sourceFile.getDefaultExportSymbol();
  if (defaultExport) {
    return defaultExport.getName();
  }

  return null;
}

/**
 * Extract CVA (class-variance-authority) variants
 */
function extractCVAVariants(sourceFile: SourceFile): VariantInfo[] {
  const variants: VariantInfo[] = [];

  // Find cva() calls
  const callExpressions = sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression);

  for (const call of callExpressions) {
    const expression = call.getExpression();
    if (expression.getText() !== 'cva') {
      continue;
    }

    const args = call.getArguments();
    if (args.length < 2) {
      continue;
    }

    const configArg = args[1];
    if (!configArg || configArg.getKind() !== SyntaxKind.ObjectLiteralExpression) {
      continue;
    }

    // Find variants property
    const configObj = configArg.asKind(SyntaxKind.ObjectLiteralExpression);
    if (!configObj) {
      continue;
    }

    const variantsProp = configObj.getProperty('variants');
    if (!variantsProp || variantsProp.getKind() !== SyntaxKind.PropertyAssignment) {
      continue;
    }

    const variantsValue = variantsProp.asKind(SyntaxKind.PropertyAssignment)?.getInitializer();
    if (!variantsValue || variantsValue.getKind() !== SyntaxKind.ObjectLiteralExpression) {
      continue;
    }

    const variantsObj = variantsValue.asKind(SyntaxKind.ObjectLiteralExpression);
    if (!variantsObj) {
      continue;
    }

    // Extract each variant
    for (const prop of variantsObj.getProperties()) {
      if (prop.getKind() !== SyntaxKind.PropertyAssignment) {
        continue;
      }

      const propAssignment = prop.asKind(SyntaxKind.PropertyAssignment);
      if (!propAssignment) {
        continue;
      }

      const variantName = propAssignment.getName();
      const variantValue = propAssignment.getInitializer();

      if (!variantValue || variantValue.getKind() !== SyntaxKind.ObjectLiteralExpression) {
        continue;
      }

      const variantObj = variantValue.asKind(SyntaxKind.ObjectLiteralExpression);
      if (!variantObj) {
        continue;
      }

      const options = variantObj.getProperties().map((p) => p.getName().replaceAll(/['"]/g, ''));

      variants.push({
        name: variantName,
        options,
      });
    }

    // Find defaultVariants
    const defaultVariantsProp = configObj.getProperty('defaultVariants');
    if (defaultVariantsProp && defaultVariantsProp.getKind() === SyntaxKind.PropertyAssignment) {
      const defaultValue = defaultVariantsProp
        .asKind(SyntaxKind.PropertyAssignment)
        ?.getInitializer();
      if (defaultValue && defaultValue.getKind() === SyntaxKind.ObjectLiteralExpression) {
        const defaultObj = defaultValue.asKind(SyntaxKind.ObjectLiteralExpression);
        if (defaultObj) {
          for (const prop of defaultObj.getProperties()) {
            if (prop.getKind() !== SyntaxKind.PropertyAssignment) {
              continue;
            }
            const propAssignment = prop.asKind(SyntaxKind.PropertyAssignment);
            if (!propAssignment) {
              continue;
            }

            const name = propAssignment.getName();
            const value = propAssignment.getInitializer()?.getText().replaceAll(/['"]/g, '');

            const variant = variants.find((v) => v.name === name);
            if (variant && value) {
              variant.defaultValue = value;
            }
          }
        }
      }
    }
  }

  return variants;
}

/**
 * Extract component props from interface/type definition
 */
function extractComponentProps(sourceFile: SourceFile, componentName: string): PropInfo[] {
  const props: PropInfo[] = [];

  // Look for props interface (e.g., ButtonProps, InputProps)
  const propsInterfaceName = `${componentName}Props`;
  const interfaces = sourceFile.getInterfaces();

  for (const iface of interfaces) {
    if (iface.getName() === propsInterfaceName) {
      for (const prop of iface.getProperties()) {
        const name = prop.getName();
        const type = prop.getType().getText();
        const required = !prop.hasQuestionToken();

        props.push({
          name,
          required,
          type,
        });
      }
      break;
    }
  }

  // Look for type aliases
  const typeAliases = sourceFile.getTypeAliases();
  for (const typeAlias of typeAliases) {
    if (typeAlias.getName() === propsInterfaceName) {
      const type = typeAlias.getType();
      const typeProperties = type.getProperties();

      for (const prop of typeProperties) {
        const name = prop.getName();
        const propType = prop.getTypeAtLocation(typeAlias);
        const required = !prop.hasFlags(1); // Optional flag

        props.push({
          name,
          required,
          type: propType.getText(),
        });
      }
      break;
    }
  }

  return props;
}

/**
 * Determine if component is default or named export
 */
function getExportType(sourceFile: SourceFile, componentName: string): 'default' | 'named' {
  const defaultExport = sourceFile.getDefaultExportSymbol();
  if (defaultExport && defaultExport.getName() === componentName) {
    return 'default';
  }
  return 'named';
}

/**
 * Batch analyze multiple component files
 */
export function analyzeComponents(filePaths: string[]): ComponentInfo[] {
  const results: ComponentInfo[] = [];

  for (const filePath of filePaths) {
    try {
      const info = analyzeComponent(filePath);
      if (info) {
        results.push(info);
      }
    } catch (error) {}
  }

  return results;
}
