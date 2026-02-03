import React from "react";

interface FullScreenPageProps {
	children: React.ReactNode;
}

export const FullScreenPage = function FullScreenPage({
	children,
}: FullScreenPageProps) {
	return (
		<div className="fixed inset-0 z-[100] bg-background overflow-auto">
			{children}
		</div>
	);
};
