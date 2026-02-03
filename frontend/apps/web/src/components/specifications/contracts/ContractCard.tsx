import type { Contract } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@tracertm/ui";
import { motion } from "framer-motion";
import {
	ArrowRight,
	Code,
	FileCode,
	GitBranch,
	Shield,
	ShieldAlert,
	ShieldCheck,
} from "lucide-react";
import { VerificationBadge } from "./VerificationBadge";

interface ContractCardProps {
	contract: Contract;
	onClick?: () => void;
	className?: string;
	isSelected?: boolean;
}

/**
 * Status color mapping
 */
interface StatusColorMap {
	draft: string;
	active: string;
	verified: string;
	violated: string;
	deprecated: string;
}

/**
 * Icon component type
 */
type IconComponent = typeof FileCode;

/**
 * Status icon mapping
 */
interface StatusIconMap {
	draft: IconComponent;
	active: IconComponent;
	verified: IconComponent;
	violated: IconComponent;
	deprecated: IconComponent;
}

/**
 * Type icon labels
 */
type TypeIconMap = Record<string, string>;

const statusColors: StatusColorMap = {
	active: "bg-blue-500/10 text-blue-500 border-blue-500/20",
	deprecated: "bg-orange-500/10 text-orange-500 border-orange-500/20",
	draft: "bg-gray-500/10 text-gray-500 border-gray-500/20",
	verified: "bg-green-500/10 text-green-500 border-green-500/20",
	violated: "bg-red-500/10 text-red-500 border-red-500/20",
};

const statusIcons: StatusIconMap = {
	active: Shield,
	deprecated: Shield,
	draft: FileCode,
	verified: ShieldCheck,
	violated: ShieldAlert,
};

const typeIcons: TypeIconMap = {
	api: "API",
	data: "∑",
	function: "fn",
	integration: "⟷",
	invariant: "∀",
};

export function ContractCard({
	contract,
	onClick,
	className,
	isSelected = false,
}: ContractCardProps) {
	const StatusIcon = statusIcons[contract.status] || Shield;
	const totalConditions =
		(contract.preconditions?.length || 0) +
		(contract.postconditions?.length || 0) +
		(contract.invariants?.length || 0);

	const verificationStatus = contract.verificationResult?.status || "unknown";
	const passedCount = contract.verificationResult?.passedConditions || 0;
	const failedCount = contract.verificationResult?.failedConditions || 0;

	return (
		<motion.div
			initial={{ opacity: 0, y: 10 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.2 }}
		>
			<Card
				className={`hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer border-2 ${
					isSelected ? "border-primary bg-primary/5" : "border-border"
				} ${className}`}
				onClick={onClick}
			>
				<CardHeader className="pb-2">
					<div className="flex justify-between items-start gap-2">
						<div className="flex items-center gap-2 min-w-0 flex-1">
							<Badge
								variant="outline"
								className="font-mono text-xs flex-shrink-0"
							>
								{contract.contractNumber}
							</Badge>
							<motion.div
								whileHover={{ scale: 1.05 }}
								className={statusColors[contract.status]}
							>
								<Badge className={statusColors[contract.status]}>
									<StatusIcon className="w-3 h-3 mr-1" />
									{contract.status}
								</Badge>
							</motion.div>
						</div>
						<Badge variant="secondary" className="text-[10px] flex-shrink-0">
							{typeIcons[contract.contractType] || contract.contractType}
						</Badge>
					</div>
					<CardTitle className="text-base mt-2 truncate">
						{contract.title}
					</CardTitle>
				</CardHeader>

				<CardContent className="pb-4 space-y-3">
					{contract.description && (
						<p className="text-sm text-muted-foreground line-clamp-2">
							{contract.description}
						</p>
					)}

					{/* Condition Counts */}
					<div className="flex gap-3 text-xs text-muted-foreground">
						<div className="flex items-center gap-1">
							<Shield className="w-3.5 h-3.5 text-blue-600" />
							<span>
								<span className="font-bold text-foreground">
									{contract.preconditions?.length || 0}
								</span>
								<span className="hidden sm:inline"> pre</span>
							</span>
						</div>
						<div className="flex items-center gap-1">
							<Shield className="w-3.5 h-3.5 text-green-600" />
							<span>
								<span className="font-bold text-foreground">
									{contract.postconditions?.length || 0}
								</span>
								<span className="hidden sm:inline"> post</span>
							</span>
						</div>
						<div className="flex items-center gap-1">
							<Shield className="w-3.5 h-3.5 text-purple-600" />
							<span>
								<span className="font-bold text-foreground">
									{contract.invariants?.length || 0}
								</span>
								<span className="hidden sm:inline"> inv</span>
							</span>
						</div>
					</div>

					{/* State Machine Info */}
					{contract.states && contract.states.length > 0 && (
						<div className="flex items-center gap-1.5 text-xs text-muted-foreground px-2 py-1.5 bg-muted/50 rounded">
							<GitBranch className="w-3 h-3" />
							<span>
								{contract.states.length} state
								{contract.states.length !== 1 ? "s" : ""}
							</span>
						</div>
					)}
				</CardContent>

				<CardFooter className="pt-0 flex justify-between items-center text-xs text-muted-foreground gap-2">
					<div className="flex items-center gap-1.5">
						{contract.executableSpec && (
							<Badge variant="outline" className="text-[10px] h-5 px-1.5 gap-1">
								<Code className="w-3 h-3" />
								<span className="hidden sm:inline">Executable</span>
							</Badge>
						)}
					</div>

					{/* Verification Status */}
					{totalConditions > 0 && (
						<VerificationBadge
							status={
								verificationStatus === "pass"
									? "pass"
									: (verificationStatus === "fail"
										? "fail"
										: "unknown")
							}
							lastVerifiedAt={contract.lastVerifiedAt}
							passedCount={passedCount}
							failedCount={failedCount}
							totalCount={totalConditions}
							showTimestamp
							showDetails
						/>
					)}

					<Button
						variant="ghost"
						size="sm"
						className="h-8 gap-1 hover:bg-muted/50 transition-colors flex-shrink-0 ml-auto"
					>
						<ArrowRight className="w-3 h-3" />
					</Button>
				</CardFooter>
			</Card>
		</motion.div>
	);
}
