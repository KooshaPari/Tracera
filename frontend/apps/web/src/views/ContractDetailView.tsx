import { useNavigate, useParams } from "@tanstack/react-router";
import { Button, Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import { format } from "date-fns";
import { ArrowLeft } from "lucide-react";
import { ConditionList } from "@/components/specifications/contracts/ConditionList";
import { ContractCard } from "@/components/specifications/contracts/ContractCard";
import { StateMachineViewer } from "@/components/specifications/contracts/StateMachineViewer";
import { useContract, useContractActivities } from "@/hooks/useSpecifications";

export function ContractDetailView() {
	const params = useParams({ strict: false }) as {
		projectId?: string;
		contractId?: string;
	};
	const navigate = useNavigate();
	const contractId = params.contractId || "";
	const { data: contract, isLoading } = useContract(contractId);
	const { data: contractActivities } = useContractActivities(contractId);

	if (isLoading) {
		return (
			<div className="p-6 space-y-6">
				<div className="h-8 w-40 bg-muted/40 rounded" />
				<div className="h-32 bg-muted/30 rounded-xl" />
				<div className="h-64 bg-muted/20 rounded-xl" />
			</div>
		);
	}

	if (!contract) {
		return (
			<div className="p-6 space-y-4">
				<Button
					variant="ghost"
					onClick={() =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: params.projectId || "" },
							search: { tab: "contracts" },
						})
					}
				>
					<ArrowLeft className="h-4 w-4 mr-2" />
					Back to Contracts
				</Button>
				<Card className="border-none bg-muted/20">
					<CardHeader>
						<CardTitle>Contract not found</CardTitle>
					</CardHeader>
					<CardContent className="text-sm text-muted-foreground">
						This contract may have been deleted or you don’t have access.
					</CardContent>
				</Card>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-6">
			<div className="flex items-center justify-between">
				<Button
					variant="ghost"
					onClick={() =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: params.projectId || "" },
							search: { tab: "contracts" },
						})
					}
				>
					<ArrowLeft className="h-4 w-4 mr-2" />
					Back to Contracts
				</Button>
			</div>

			<ContractCard contract={contract} className="cursor-default" />

			<Card className="border-none bg-card/50">
				<CardHeader>
					<CardTitle className="text-base">Activity</CardTitle>
				</CardHeader>
				<CardContent className="space-y-3 text-sm text-muted-foreground">
					{contractActivities && contractActivities.length > 0
						? contractActivities.map((activity) => (
								<div
									key={activity.id}
									className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0"
								>
									<div>
										<div className="font-medium text-foreground">
											{activity.activityType}
										</div>
										<div className="text-xs text-muted-foreground">
											{activity.description || "Contract updated"}
										</div>
									</div>
									<div className="text-xs text-muted-foreground">
										{activity.createdAt
											? format(
													new Date(activity.createdAt),
													"MMM d, yyyy HH:mm",
												)
											: "—"}
									</div>
								</div>
							))
						: [
								contract.createdAt
									? {
											label: "Created",
											detail: `Contract ${contract.contractNumber}`,
											date: contract.createdAt,
										}
									: null,
								contract.updatedAt
									? {
											label: "Updated",
											detail: "Metadata updated",
											date: contract.updatedAt,
										}
									: null,
								contract.lastVerifiedAt
									? {
											label: "Verified",
											detail:
												contract.verificationResult?.status === "pass"
													? "All conditions passed"
													: contract.verificationResult?.status === "fail"
														? "Verification failed"
														: "Verification run",
											date: contract.lastVerifiedAt,
										}
									: null,
							]
								.filter(Boolean)
								.map((entry: any) => (
									<div
										key={`${entry.label}-${entry.date}`}
										className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0"
									>
										<div>
											<div className="font-medium text-foreground">
												{entry.label}
											</div>
											<div className="text-xs text-muted-foreground">
												{entry.detail}
											</div>
										</div>
										<div className="text-xs text-muted-foreground">
											{format(new Date(entry.date), "MMM d, yyyy HH:mm")}
										</div>
									</div>
								))}
					{(!contractActivities || contractActivities.length === 0) &&
						!contract.createdAt &&
						!contract.updatedAt &&
						!contract.lastVerifiedAt && <div>No activity yet.</div>}
				</CardContent>
			</Card>

			<ConditionList
				preconditions={contract.preconditions}
				postconditions={contract.postconditions}
				invariants={contract.invariants}
			/>

			{contract.states && contract.states.length > 0 && (
				<Card className="border-none bg-card/50">
					<CardHeader>
						<CardTitle className="text-base">State Machine</CardTitle>
					</CardHeader>
					<CardContent>
						<StateMachineViewer
							states={contract.states}
							transitions={contract.transitions || []}
							initialState={contract.initialState}
						/>
					</CardContent>
				</Card>
			)}
		</div>
	);
}
