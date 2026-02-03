/**
 * Enterprise Button Component
 *
 * Professional button with subtle animations, loading states, and micro-interactions
 * Matches enterprise applications like Salesforce, Jira, Linear
 */

import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import type { VariantProps } from "class-variance-authority";
import { motion } from "framer-motion";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
	"inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
	{
		defaultVariants: {
			size: "default",
			variant: "default",
		},
		variants: {
			size: {
				default: "h-10 px-4 py-2",
				sm: "h-9 rounded-md px-3",
				lg: "h-11 rounded-md px-8",
				icon: "h-10 w-10",
				xs: "h-7 rounded px-2 text-xs",
				xl: "h-13 rounded-lg px-10 text-base",
			},
			variant: {
				default: "bg-primary text-primary-foreground hover:bg-primary/90",
				destructive:
					"bg-destructive text-destructive-foreground hover:bg-destructive/90",
				outline:
					"border border-input bg-background hover:bg-accent hover:text-accent-foreground",
				secondary:
					"bg-secondary text-secondary-foreground hover:bg-secondary/80",
				ghost: "hover:bg-accent hover:text-accent-foreground",
				link: "text-primary underline-offset-4 hover:underline",

				// Enterprise variants
				enterprise:
					"bg-gradient-to-r from-primary to-primary/90 text-primary-foreground shadow-sm hover:from-primary/90 hover:to-primary/80 hover:shadow-md",
				success:
					"bg-green-600 text-white hover:bg-green-700 focus:ring-green-500",
				warning:
					"bg-amber-600 text-white hover:bg-amber-700 focus:ring-amber-500",
				info: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
			},
		},
	},
);

export interface ButtonProps
	extends React.ButtonHTMLAttributes<HTMLButtonElement>,
		VariantProps<typeof buttonVariants> {
	asChild?: boolean;
	loading?: boolean;
	success?: boolean;
	iconLeft?: React.ReactNode;
	iconRight?: React.ReactNode;
	ripple?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
	(
		{
			className,
			variant,
			size,
			asChild = false,
			loading = false,
			success = false,
			iconLeft,
			iconRight,
			ripple = true,
			children,
			disabled,
			...props
		},
		ref,
	) => {
		const Comp = asChild ? Slot : motion.button;

		return (
			<Comp
				className={cn(
					buttonVariants({ className, size, variant }),
					loading && "relative overflow-hidden",
					success && variant === "default" && "bg-green-600 hover:bg-green-700",
					"cursor-pointer",
				)}
				ref={ref}
				disabled={disabled || loading}
				whileHover={{ scale: 1.02 }}
				whileTap={{ scale: 0.98 }}
				transition={{ damping: 17, stiffness: 400, type: "spring" }}
				{...(props.style ? { style: props.style as React.CSSProperties } : {})}
				{...(Object.fromEntries(
					Object.entries(props).filter(([key]) => key !== "style"),
				) as any)}
			>
				{/* Ripple effect */}
				{ripple && !loading && !success && (
					<span className="absolute inset-0 overflow-hidden rounded-md pointer-events-none">
						<span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300 transform -skew-x-12 -translate-x-full hover:translate-x-full" />
					</span>
				)}

				{/* Loading state */}
				{loading && (
					<motion.div
						className="absolute inset-0 flex items-center justify-center bg-black/10 rounded-md"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
					>
						<div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
					</motion.div>
				)}

				{/* Success state */}
				{success && (
					<motion.div
						className="absolute inset-0 flex items-center justify-center bg-green-500/10 rounded-md"
						initial={{ opacity: 0, scale: 0.8 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ duration: 0.3, type: "spring" }}
					>
						<svg
							className="h-5 w-5 text-green-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<motion.path
								strokeLinecap="round"
								strokeLinejoin="round"
								strokeWidth={2}
								d="M5 13l4 4L19 7"
								initial={{ pathLength: 0 }}
								animate={{ pathLength: 1 }}
								transition={{ delay: 0.2, duration: 0.3 }}
							/>
						</svg>
					</motion.div>
				)}

				{/* Content */}
				<span className={cn("flex items-center gap-2", loading && "opacity-0")}>
					{iconLeft}
					{children}
					{iconRight}
				</span>
			</Comp>
		);
	},
);

Button.displayName = "Button";

// Enterprise button group
export interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
	children: React.ReactNode;
	variant?: "default" | "segmented" | "toolbar";
	size?: "default" | "sm" | "lg";
}

export const ButtonGroup = React.forwardRef<HTMLDivElement, ButtonGroupProps>(
	(
		{
			children,
			variant = "default",
			size: _size = "default",
			className,
			...props
		},
		ref,
	) => (
		<div
			ref={ref}
			className={cn(
				"inline-flex",
				{
					// Default vertical grouping
					"flex-col": variant === "default",
					// Segmented horizontal buttons
					"items-center rounded-md shadow-sm": variant === "segmented",
					// ToolBar spacing
					"items-center gap-1": variant === "toolbar",
				},
				className,
			)}
			{...props}
		>
			{variant === "segmented" &&
				React.Children.map(children, (child, index) => {
					if (React.isValidElement(child)) {
						const childProps = child.props as { className?: string };
						return React.cloneElement(child, {
							className: cn(
								index === 0 && "rounded-l-md rounded-r-none",
								index === React.Children.count(children) - 1 &&
									"rounded-r-md rounded-l-none",
								index !== 0 &&
									index !== React.Children.count(children) - 1 &&
									"rounded-none",
								childProps.className,
							),
						} as any);
					}
					return child;
				})}
			{variant !== "segmented" && children}
		</div>
	),
);

ButtonGroup.displayName = "ButtonGroup";

// Toolbar button with keyboard shortcuts
export interface ToolbarButtonProps extends Omit<ButtonProps, "size"> {
	shortcut?: string;
	tooltip?: string;
}

export const ToolbarButton = React.forwardRef<
	HTMLButtonElement,
	ToolbarButtonProps
>(({ shortcut, tooltip, children, className, ...props }, ref) => (
	<Button
		ref={ref}
		size="sm"
		variant="ghost"
		className={cn("h-8 px-3 group relative", className)}
		{...props}
	>
		<div className="flex items-center gap-2">
			{children}
			{shortcut && (
				<kbd className="hidden md:inline-flex items-center px-1.5 py-0.5 font-mono text-xs text-muted-foreground bg-muted rounded">
					{shortcut}
				</kbd>
			)}
		</div>

		{tooltip && (
			<div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs text-white bg-black/80 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
				{tooltip}
				<div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
					<div className="border-4 border-transparent border-t-black/80" />
				</div>
			</div>
		)}
	</Button>
));

ToolbarButton.displayName = "ToolbarButton";

export { Button, buttonVariants };
export default Button;
