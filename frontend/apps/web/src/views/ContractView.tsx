import { useParams } from "@tanstack/react-router";
import { Button } from "@tracertm/ui";
import { Plus } from "lucide-react";
import { ContractCard } from "@/components/specifications/contracts/ContractCard";
import { useContracts } from "@/hooks/useSpecifications";

export function ContractView() {
	const { projectId } = useParams({ strict: false });
	const { data: contractsData } = useContracts({ projectId: projectId || "" });
	const contracts = contractsData?.contracts ?? [];

	return (
		<div className="p-6 space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h1 className="text-2xl font-bold">Contracts</h1>
					<p className="text-muted-foreground">
						Formal specifications and design-by-contract definitions.
					</p>
				</div>
				<Button>
					<Plus className="w-4 h-4 mr-2" />
					New Contract
				</Button>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{contracts.map((contract) => (
					<ContractCard key={contract.id} contract={contract} />
				))}
			</div>
		</div>
	);
}
