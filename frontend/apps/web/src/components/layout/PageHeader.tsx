import type { ReactNode } from "react";

interface PageHeaderProps {
	title: string;
	description?: string;
	icon?: ReactNode;
	actions?: ReactNode;
	breadcrumbs?: Array<{ label: string; href?: string }>;
}

export function PageHeader({
	title,
	description,
	icon,
	actions,
	breadcrumbs,
}: PageHeaderProps) {
	return (
		<div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 transition-colors duration-200 ease-out">
			<div className="px-6 py-4">
				{breadcrumbs && breadcrumbs.length > 0 && (
					<nav className="flex mb-2" aria-label="Breadcrumb">
						<ol className="flex items-center space-x-2 text-sm">
							{breadcrumbs.map((crumb, index) => (
								<li key={index} className="flex items-center">
									{index > 0 && (
										<svg
											className="w-4 h-4 mx-2 text-gray-400"
											fill="currentColor"
											viewBox="0 0 20 20"
										>
											<path
												fillRule="evenodd"
												d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
												clipRule="evenodd"
											/>
										</svg>
									)}
									{crumb.href ? (
										<a
											href={crumb.href}
											className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors duration-200 ease-out"
										>
											{crumb.label}
										</a>
									) : (
										<span className="text-gray-900 dark:text-gray-100 font-medium">
											{crumb.label}
										</span>
									)}
								</li>
							))}
						</ol>
					</nav>
				)}

				<div className="flex items-start justify-between">
					<div className="flex items-start space-x-3">
						{icon && (
							<div className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-lg bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400">
								{icon}
							</div>
						)}
						<div>
							<h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
								{title}
							</h1>
							{description && (
								<p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
									{description}
								</p>
							)}
						</div>
					</div>

					{actions && (
						<div className="flex items-center space-x-2">{actions}</div>
					)}
				</div>
			</div>
		</div>
	);
}
