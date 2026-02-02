import { type FC } from "react";
import type { Contract } from "../../..";
import {
	Card,
	Card,
	type CardProps,
	CheckCircle2,
	type LucideIcon,
	Shield,
	ShieldAlert,
	ShieldCheck,
} from "lucide-react";

interface VerificationSummaryCardProps extends CardProps {
	label: string;
	value: string | number;
	icon: LucideIcon;
	iconClassName?: string;
}

const VerificationSummaryCard: FC<VerificationSummaryCardProps> = ({
	label,
	value,
	icon: Icon,
	iconClassName = "text-foreground",
	...props
}) => (
	<Card {...props}>
		<div className="p-4 space-y-2">
			<div className="flex items-center justify-between">
				<span className="text-xs font-medium text-muted-foreground">{label}</span>
				<Icon className={`h-4 w-4 ${iconClassName}`} />
			</div>
			<div className="text-2xl font-bold">{value}</div>
		</div>
	</Card>
);

interface VerificationSummaryCardsProps {
	contracts: Contract[];
}

export const VerificationSummaryCards: FC<VerificationSummaryCardsProps> = ({ contracts }) => {
	const total = contracts.length;
	const verified = contracts.filter((contract) => contract.status === "verified").length;
	const violated = contracts.filter((contract) => contract.status === "violated").length;
	const passRate = total > 0 ? ((verified / total) * 100).toFixed(1) : "0";

	return (
		<div className="grid gap-4 md:grid-cols-4">
			<VerificationSummaryCard
				className="border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20"
				label="Total Contracts"
				value={total}
				icon={Shield}
				iconClassName="text-blue-600"
			/>
			<VerificationSummaryCard
				className="border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20"
				label="Verified"
				value={verified}
				icon={ShieldCheck}
				iconClassName="text-green-600"
			/>
			<VerificationSummaryCard
				className="border-none bg-gradient-to-br from-red-50 to-red-100/50 dark:from-red-950/20 dark:to-red-900/20"
				label="Violated"
				value={violated}
				icon={ShieldAlert}
				iconClassName="text-red-600"
			/>
			<VerificationSummaryCard
				className="border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20"
				label="Pass Rate"
				value={`${passRate}%`}
				icon={CheckCircle2}
				iconClassName="text-purple-600"
			/>
		</div>
	);
};
