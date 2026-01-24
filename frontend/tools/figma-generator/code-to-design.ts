/**
 * Code to Design Converter
 *
 * Converts React components with Tailwind styles to Figma-compatible node structures
 */

import * as fs from "fs/promises";
import * as path from "path";
import * as ts from "typescript";

export interface FigmaNode {
	id: string;
	name: string;
	type: FigmaNodeType;
	children?: FigmaNode[];
	properties: FigmaNodeProperties;
	styles: FigmaNodeStyles;
}

export type FigmaNodeType =
	| "FRAME"
	| "GROUP"
	| "TEXT"
	| "RECTANGLE"
	| "ELLIPSE"
	| "VECTOR"
	| "COMPONENT"
	| "INSTANCE";

export interface FigmaNodeProperties {
	width?: number | "auto";
	height?: number | "auto";
	x?: number;
	y?: number;
	visible?: boolean;
	locked?: boolean;
	opacity?: number;
	blendMode?: string;
}

export interface FigmaNodeStyles {
	backgroundColor?: string;
	fills?: FigmaFill[];
	strokes?: FigmaStroke[];
	cornerRadius?: number;
	effects?: FigmaEffect[];
	layoutMode?: "HORIZONTAL" | "VERTICAL" | "NONE";
	padding?: { top: number; right: number; bottom: number; left: number };
	gap?: number;
	typography?: TypographyStyle;
}

export interface FigmaFill {
	type: "SOLID" | "GRADIENT" | "IMAGE";
	color?: string;
	opacity?: number;
	gradient?: {
		type: "LINEAR" | "RADIAL";
		stops: { position: number; color: string }[];
	};
}

export interface FigmaStroke {
	type: "SOLID";
	color: string;
	weight: number;
}

export interface FigmaEffect {
	type: "DROP_SHADOW" | "INNER_SHADOW" | "BLUR";
	color?: string;
	offset?: { x: number; y: number };
	radius: number;
	spread?: number;
}

export interface TypographyStyle {
	fontFamily: string;
	fontSize: number;
	fontWeight: number;
	lineHeight: number;
	letterSpacing?: number;
	textAlign?: "LEFT" | "CENTER" | "RIGHT";
	textDecoration?: "NONE" | "UNDERLINE" | "STRIKETHROUGH";
}

export interface ComponentDefinition {
	name: string;
	filePath: string;
	props: ComponentProp[];
	variants?: ComponentVariant[];
	nodes: FigmaNode[];
}

export interface ComponentProp {
	name: string;
	type: string;
	optional: boolean;
	defaultValue?: string;
}

export interface ComponentVariant {
	name: string;
	values: string[];
}

export interface DesignToken {
	colors: Record<string, string>;
	spacing: Record<string, number>;
	typography: Record<string, TypographyStyle>;
	borderRadius: Record<string, number>;
	shadows: Record<string, string>;
}

/**
 * Tailwind to Figma style converter
 */
export class TailwindConverter {
	private tokens: DesignToken;

	constructor(tokens?: DesignToken) {
		this.tokens = tokens || this.getDefaultTokens();
	}

	/**
	 * Parse Tailwind classes and convert to Figma styles
	 */
	parseClasses(classNames: string): FigmaNodeStyles {
		const classes = classNames.split(/\s+/).filter(Boolean);
		const styles: FigmaNodeStyles = {};

		for (const className of classes) {
			this.applyClassToStyles(className, styles);
		}

		return styles;
	}

	private applyClassToStyles(className: string, styles: FigmaNodeStyles): void {
		// Background color
		if (className.startsWith("bg-")) {
			styles.backgroundColor = this.parseColor(className.replace("bg-", ""));
		}

		// Padding
		const paddingMatch = className.match(/^p([trblxy])?-(.+)$/);
		if (paddingMatch) {
			const [, direction, value] = paddingMatch;
			const padding = this.parseSpacing(value);
			styles.padding = styles.padding || {
				top: 0,
				right: 0,
				bottom: 0,
				left: 0,
			};

			switch (direction) {
				case "t":
					styles.padding.top = padding;
					break;
				case "r":
					styles.padding.right = padding;
					break;
				case "b":
					styles.padding.bottom = padding;
					break;
				case "l":
					styles.padding.left = padding;
					break;
				case "x":
					styles.padding.left = padding;
					styles.padding.right = padding;
					break;
				case "y":
					styles.padding.top = padding;
					styles.padding.bottom = padding;
					break;
				default:
					styles.padding = {
						top: padding,
						right: padding,
						bottom: padding,
						left: padding,
					};
			}
		}

		// Gap (for flex/grid)
		if (className.startsWith("gap-")) {
			styles.gap = this.parseSpacing(className.replace("gap-", ""));
		}

		// Border radius
		if (className.startsWith("rounded")) {
			const value = className.replace("rounded-", "") || "DEFAULT";
			styles.cornerRadius = this.tokens.borderRadius[value] || 8;
		}

		// Flex/Grid layout
		if (className === "flex") {
			styles.layoutMode = "HORIZONTAL";
		}
		if (className === "flex-col") {
			styles.layoutMode = "VERTICAL";
		}

		// Typography
		if (className.startsWith("text-")) {
			const value = className.replace("text-", "");
			if (this.tokens.typography[value]) {
				styles.typography = { ...this.tokens.typography[value] };
			}
		}

		// Font weight
		if (className.startsWith("font-")) {
			const weight = this.parseFontWeight(className.replace("font-", ""));
			if (weight) {
				styles.typography = styles.typography || this.getDefaultTypography();
				styles.typography.fontWeight = weight;
			}
		}

		// Shadow
		if (className.startsWith("shadow")) {
			const shadowKey = className.replace("shadow-", "") || "DEFAULT";
			const shadowValue = this.tokens.shadows[shadowKey];
			if (shadowValue) {
				styles.effects = styles.effects || [];
				styles.effects.push(this.parseShadow(shadowValue));
			}
		}
	}

	private parseColor(colorClass: string): string {
		const colorMap: Record<string, string> = {
			transparent: "transparent",
			current: "currentColor",
			black: "#000000",
			white: "#ffffff",
		};

		if (colorMap[colorClass]) {
			return colorMap[colorClass];
		}

		// Parse color-shade format (e.g., "blue-500")
		const match = colorClass.match(/^([a-z]+)-(\d+)$/);
		if (match) {
			const [, color, shade] = match;
			return this.tokens.colors[`${color}-${shade}`] || "#000000";
		}

		return this.tokens.colors[colorClass] || "#000000";
	}

	private parseSpacing(value: string): number {
		const spacingMap: Record<string, number> = {
			"0": 0,
			"1": 4,
			"2": 8,
			"3": 12,
			"4": 16,
			"5": 20,
			"6": 24,
			"8": 32,
			"10": 40,
			"12": 48,
			"16": 64,
		};

		return spacingMap[value] || parseInt(value, 10) * 4 || 0;
	}

	private parseFontWeight(weight: string): number | null {
		const weightMap: Record<string, number> = {
			thin: 100,
			extralight: 200,
			light: 300,
			normal: 400,
			medium: 500,
			semibold: 600,
			bold: 700,
			extrabold: 800,
			black: 900,
		};

		return weightMap[weight] || null;
	}

	private parseShadow(shadowString: string): FigmaEffect {
		// Parse CSS shadow: "0 4px 6px rgba(0, 0, 0, 0.1)"
		const parts = shadowString.split(/\s+/);
		return {
			type: "DROP_SHADOW",
			offset: { x: parseInt(parts[0]) || 0, y: parseInt(parts[1]) || 0 },
			radius: parseInt(parts[2]) || 0,
			color: parts[3] || "rgba(0, 0, 0, 0.1)",
		};
	}

	private getDefaultTypography(): TypographyStyle {
		return {
			fontFamily: "Inter",
			fontSize: 16,
			fontWeight: 400,
			lineHeight: 24,
		};
	}

	private getDefaultTokens(): DesignToken {
		return {
			colors: {
				"gray-50": "#f9fafb",
				"gray-100": "#f3f4f6",
				"gray-200": "#e5e7eb",
				"gray-300": "#d1d5db",
				"gray-500": "#6b7280",
				"gray-700": "#374151",
				"gray-900": "#111827",
				"blue-500": "#3b82f6",
				"blue-600": "#2563eb",
				"green-500": "#10b981",
				"red-500": "#ef4444",
			},
			spacing: {
				"0": 0,
				"1": 4,
				"2": 8,
				"3": 12,
				"4": 16,
			},
			typography: {
				sm: {
					fontFamily: "Inter",
					fontSize: 14,
					fontWeight: 400,
					lineHeight: 20,
				},
				base: {
					fontFamily: "Inter",
					fontSize: 16,
					fontWeight: 400,
					lineHeight: 24,
				},
				lg: {
					fontFamily: "Inter",
					fontSize: 18,
					fontWeight: 400,
					lineHeight: 28,
				},
				xl: {
					fontFamily: "Inter",
					fontSize: 20,
					fontWeight: 600,
					lineHeight: 28,
				},
			},
			borderRadius: {
				DEFAULT: 8,
				sm: 4,
				md: 6,
				lg: 12,
				full: 9999,
			},
			shadows: {
				DEFAULT: "0 1px 3px rgba(0, 0, 0, 0.1)",
				md: "0 4px 6px rgba(0, 0, 0, 0.1)",
				lg: "0 10px 15px rgba(0, 0, 0, 0.1)",
			},
		};
	}
}

/**
 * Parse React component to extract structure and styles
 */
export class ComponentParser {
	private converter: TailwindConverter;

	constructor(tokens?: DesignToken) {
		this.converter = new TailwindConverter(tokens);
	}

	/**
	 * Parse TypeScript file and extract component definitions
	 */
	async parseFile(filePath: string): Promise<ComponentDefinition[]> {
		const sourceCode = await fs.readFile(filePath, "utf-8");
		const sourceFile = ts.createSourceFile(
			filePath,
			sourceCode,
			ts.ScriptTarget.Latest,
			true,
		);

		const definitions: ComponentDefinition[] = [];

		const visit = (node: ts.Node): void => {
			// Look for function components
			if (ts.isFunctionDeclaration(node) || ts.isArrowFunction(node)) {
				const component = this.extractComponent(node, filePath);
				if (component) {
					definitions.push(component);
				}
			}

			ts.forEachChild(node, visit);
		};

		visit(sourceFile);
		return definitions;
	}

	private extractComponent(
		node: ts.FunctionDeclaration | ts.ArrowFunction,
		filePath: string,
	): ComponentDefinition | null {
		const name = this.getComponentName(node);
		if (!name) return null;

		const props = this.extractProps(node);
		const nodes = this.extractNodes(node);

		return {
			name,
			filePath,
			props,
			nodes,
		};
	}

	private getComponentName(
		node: ts.FunctionDeclaration | ts.ArrowFunction,
	): string | null {
		if (ts.isFunctionDeclaration(node) && node.name) {
			return node.name.text;
		}

		// For arrow functions, look at parent variable declaration
		const parent = node.parent;
		if (ts.isVariableDeclaration(parent) && ts.isIdentifier(parent.name)) {
			return parent.name.text;
		}

		return null;
	}

	private extractProps(
		node: ts.FunctionDeclaration | ts.ArrowFunction,
	): ComponentProp[] {
		const props: ComponentProp[] = [];

		if (node.parameters.length > 0) {
			const param = node.parameters[0];
			if (param.type && ts.isTypeLiteralNode(param.type)) {
				for (const member of param.type.members) {
					if (ts.isPropertySignature(member) && ts.isIdentifier(member.name)) {
						props.push({
							name: member.name.text,
							type: member.type?.getText() || "unknown",
							optional: !!member.questionToken,
						});
					}
				}
			}
		}

		return props;
	}

	private extractNodes(
		node: ts.FunctionDeclaration | ts.ArrowFunction,
	): FigmaNode[] {
		const nodes: FigmaNode[] = [];

		const visit = (node: ts.Node): void => {
			if (ts.isJsxElement(node) || ts.isJsxSelfClosingElement(node)) {
				const figmaNode = this.jsxToFigmaNode(node);
				if (figmaNode) {
					nodes.push(figmaNode);
				}
			}

			ts.forEachChild(node, visit);
		};

		visit(node);
		return nodes;
	}

	private jsxToFigmaNode(
		node: ts.JsxElement | ts.JsxSelfClosingElement,
	): FigmaNode | null {
		const tagName = this.getJsxTagName(node);
		if (!tagName) return null;

		const className = this.getJsxClassName(node);
		const styles = className ? this.converter.parseClasses(className) : {};

		const figmaNode: FigmaNode = {
			id: this.generateId(),
			name: tagName,
			type: this.mapTagToFigmaType(tagName),
			properties: {},
			styles,
		};

		// Extract children
		if (ts.isJsxElement(node)) {
			const children: FigmaNode[] = [];
			for (const child of node.children) {
				if (ts.isJsxElement(child) || ts.isJsxSelfClosingElement(child)) {
					const childNode = this.jsxToFigmaNode(child);
					if (childNode) {
						children.push(childNode);
					}
				}
			}
			if (children.length > 0) {
				figmaNode.children = children;
			}
		}

		return figmaNode;
	}

	private getJsxTagName(
		node: ts.JsxElement | ts.JsxSelfClosingElement,
	): string | null {
		const openingElement = ts.isJsxElement(node) ? node.openingElement : node;
		if (ts.isIdentifier(openingElement.tagName)) {
			return openingElement.tagName.text;
		}
		return null;
	}

	private getJsxClassName(
		node: ts.JsxElement | ts.JsxSelfClosingElement,
	): string | null {
		const attributes = ts.isJsxElement(node)
			? node.openingElement.attributes
			: node.attributes;

		for (const attr of attributes.properties) {
			if (
				ts.isJsxAttribute(attr) &&
				ts.isIdentifier(attr.name) &&
				attr.name.text === "className" &&
				attr.initializer &&
				ts.isStringLiteral(attr.initializer)
			) {
				return attr.initializer.text;
			}
		}

		return null;
	}

	private mapTagToFigmaType(tagName: string): FigmaNodeType {
		const typeMap: Record<string, FigmaNodeType> = {
			div: "FRAME",
			span: "TEXT",
			p: "TEXT",
			h1: "TEXT",
			h2: "TEXT",
			h3: "TEXT",
			button: "FRAME",
			img: "RECTANGLE",
		};

		return typeMap[tagName.toLowerCase()] || "FRAME";
	}

	private generateId(): string {
		return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}
}

/**
 * Convert component definitions to Figma-compatible format
 */
export async function componentsToFigma(
	componentFiles: string[],
	tokens?: DesignToken,
): Promise<ComponentDefinition[]> {
	const parser = new ComponentParser(tokens);
	const allDefinitions: ComponentDefinition[] = [];

	for (const file of componentFiles) {
		const definitions = await parser.parseFile(file);
		allDefinitions.push(...definitions);
	}

	return allDefinitions;
}
