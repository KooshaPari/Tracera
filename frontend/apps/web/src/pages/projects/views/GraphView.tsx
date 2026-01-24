import cytoscape, { type Core, type NodeSingular } from "cytoscape";
import { Maximize2, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

// Sample data matching TraceRTM schema
const nodes = [
	// Features (purple)
	{
		data: {
			id: "f1",
			label: "User Authentication",
			type: "feature",
			status: "done",
		},
	},
	{
		data: {
			id: "f2",
			label: "Project Management",
			type: "feature",
			status: "in_progress",
		},
	},
	{
		data: {
			id: "f3",
			label: "Traceability Links",
			type: "feature",
			status: "todo",
		},
	},
	{
		data: {
			id: "f4",
			label: "Multi-View System",
			type: "feature",
			status: "in_progress",
		},
	},
	// Code modules (blue)
	{ data: { id: "c1", label: "auth.py", type: "code", status: "done" } },
	{
		data: {
			id: "c2",
			label: "projects.py",
			type: "code",
			status: "in_progress",
		},
	},
	{ data: { id: "c3", label: "links.py", type: "code", status: "todo" } },
	{ data: { id: "c4", label: "views.py", type: "code", status: "done" } },
	{
		data: { id: "c5", label: "items.py", type: "code", status: "in_progress" },
	},
	// Tests (green)
	{ data: { id: "t1", label: "test_auth.py", type: "test", status: "done" } },
	{
		data: {
			id: "t2",
			label: "test_projects.py",
			type: "test",
			status: "in_progress",
		},
	},
	{ data: { id: "t3", label: "test_links.py", type: "test", status: "todo" } },
	{ data: { id: "t4", label: "test_e2e.py", type: "test", status: "done" } },
];

const edges = [
	// Feature → Code (implements)
	{ data: { id: "e1", source: "f1", target: "c1", type: "implements" } },
	{ data: { id: "e2", source: "f2", target: "c2", type: "implements" } },
	{ data: { id: "e3", source: "f2", target: "c5", type: "implements" } },
	{ data: { id: "e4", source: "f3", target: "c3", type: "implements" } },
	{ data: { id: "e5", source: "f4", target: "c4", type: "implements" } },
	// Code → Test (tests)
	{ data: { id: "e6", source: "c1", target: "t1", type: "tests" } },
	{ data: { id: "e7", source: "c2", target: "t2", type: "tests" } },
	{ data: { id: "e8", source: "c3", target: "t3", type: "tests" } },
	{ data: { id: "e9", source: "c1", target: "t4", type: "tests" } },
	{ data: { id: "e10", source: "c2", target: "t4", type: "tests" } },
	// Dependencies
	{ data: { id: "e11", source: "f3", target: "f2", type: "depends_on" } },
	{ data: { id: "e12", source: "c5", target: "c2", type: "depends_on" } },
];

const typeColors: Record<string, string> = {
	feature: "#9333ea", // purple
	code: "#3b82f6", // blue
	test: "#22c55e", // green
};

const statusOpacity: Record<string, number> = {
	done: 1,
	in_progress: 0.8,
	todo: 0.5,
};

export function GraphView() {
	const containerRef = useRef<HTMLDivElement>(null);
	const cyRef = useRef<Core | null>(null);
	const [selectedNode, setSelectedNode] = useState<NodeSingular | null>(null);
	const [layout, setLayout] = useState<"cose" | "dagre" | "circle">("cose");
	const [filterType, setFilterType] = useState<string | null>(null);

	const initCytoscape = useCallback(() => {
		if (!containerRef.current) return;

		const filteredNodes = filterType
			? nodes.filter((n) => n.data.type === filterType)
			: nodes;

		const filteredNodeIds = new Set(filteredNodes.map((n) => n.data.id));
		const filteredEdges = edges.filter(
			(e) =>
				filteredNodeIds.has(e.data.source) &&
				filteredNodeIds.has(e.data.target),
		);

		cyRef.current = cytoscape({
			container: containerRef.current,
			elements: [...filteredNodes, ...filteredEdges],
			style: [
				{
					selector: "node",
					style: {
						"background-color": (ele: any) =>
							typeColors[ele.data("type")] || "#666",
						"background-opacity": (ele: any) =>
							statusOpacity[ele.data("status")] || 1,
						label: "data(label)",
						color: "#fff",
						"text-outline-color": (ele: any) =>
							typeColors[ele.data("type")] || "#666",
						"text-outline-width": 2,
						"font-size": 12,
						width: 50,
						height: 50,
						"text-valign": "bottom",
						"text-margin-y": 5,
					},
				},
				{
					selector: "edge",
					style: {
						width: 2,
						"line-color": "#94a3b8",
						"target-arrow-color": "#94a3b8",
						"target-arrow-shape": "triangle",
						"curve-style": "bezier",
						opacity: 0.7,
					},
				},
				{
					selector: 'edge[type="implements"]',
					style: { "line-color": "#9333ea", "target-arrow-color": "#9333ea" },
				},
				{
					selector: 'edge[type="tests"]',
					style: { "line-color": "#22c55e", "target-arrow-color": "#22c55e" },
				},
				{
					selector: 'edge[type="depends_on"]',
					style: {
						"line-color": "#f59e0b",
						"target-arrow-color": "#f59e0b",
						"line-style": "dashed",
					},
				},
				{
					selector: "node:selected",
					style: {
						"border-width": 4,
						"border-color": "#fff",
						"overlay-opacity": 0.2,
					},
				},
			],
			layout: { name: layout, animate: true, animationDuration: 500 },
			minZoom: 0.2,
			maxZoom: 3,
		});

		cyRef.current.on("tap", "node", (evt) => setSelectedNode(evt.target));
		cyRef.current.on("tap", (evt) => {
			if (evt.target === cyRef.current) setSelectedNode(null);
		});
	}, [layout, filterType]);

	useEffect(() => {
		initCytoscape();
		return () => {
			cyRef.current?.destroy();
		};
	}, [initCytoscape]);

	const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.2);
	const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() / 1.2);
	const handleFit = () => cyRef.current?.fit(undefined, 50);
	const handleReset = () => {
		setFilterType(null);
		setLayout("cose");
	};

	return (
		<div className="space-y-4">
			<div className="flex items-center justify-between">
				<h3 className="text-lg font-semibold">Traceability Graph</h3>
				<div className="flex items-center gap-2">
					<select
						value={layout}
						onChange={(e) =>
							setLayout((e.target as HTMLSelectElement).value as typeof layout)
						}
						className="rounded-md border px-2 py-1 text-sm"
					>
						<option value="cose">Force-directed</option>
						<option value="circle">Circle</option>
						<option value="dagre">Hierarchical</option>
					</select>
					<select
						value={filterType || ""}
						onChange={(e) =>
							setFilterType((e.target as HTMLSelectElement).value || null)
						}
						className="rounded-md border px-2 py-1 text-sm"
					>
						<option value="">All Types</option>
						<option value="feature">Features</option>
						<option value="code">Code</option>
						<option value="test">Tests</option>
					</select>
					<div className="flex gap-1 rounded-md border p-1">
						<button
							onClick={handleZoomIn}
							className="rounded p-1 hover:bg-accent"
						>
							<ZoomIn className="h-4 w-4" />
						</button>
						<button
							onClick={handleZoomOut}
							className="rounded p-1 hover:bg-accent"
						>
							<ZoomOut className="h-4 w-4" />
						</button>
						<button onClick={handleFit} className="rounded p-1 hover:bg-accent">
							<Maximize2 className="h-4 w-4" />
						</button>
						<button
							onClick={handleReset}
							className="rounded p-1 hover:bg-accent"
						>
							<RotateCcw className="h-4 w-4" />
						</button>
					</div>
				</div>
			</div>

			<div className="flex gap-4">
				<div
					ref={containerRef}
					className="h-[600px] flex-1 rounded-lg border bg-slate-950"
				/>

				{selectedNode && (
					<div className="w-64 rounded-lg border bg-card p-4">
						<h4 className="font-semibold">{selectedNode.data("label")}</h4>
						<div className="mt-3 space-y-2 text-sm">
							<div className="flex justify-between">
								<span className="text-muted-foreground">Type</span>
								<span
									className="rounded px-2 py-0.5 text-xs font-medium"
									style={{
										backgroundColor: `${typeColors[selectedNode.data("type")]}20`,
										color: typeColors[selectedNode.data("type")],
									}}
								>
									{selectedNode.data("type")}
								</span>
							</div>
							<div className="flex justify-between">
								<span className="text-muted-foreground">Status</span>
								<span>{selectedNode.data("status")}</span>
							</div>
							<div className="flex justify-between">
								<span className="text-muted-foreground">Connections</span>
								<span>{selectedNode.connectedEdges().length}</span>
							</div>
						</div>
						<div className="mt-4 border-t pt-3">
							<p className="text-xs text-muted-foreground">Connected to:</p>
							<ul className="mt-1 space-y-1 text-sm">
								{selectedNode.neighborhood("node").map((n: NodeSingular) => (
									<li key={n.id()} className="flex items-center gap-2">
										<span
											className="h-2 w-2 rounded-full"
											style={{ backgroundColor: typeColors[n.data("type")] }}
										/>
										{n.data("label")}
									</li>
								))}
							</ul>
						</div>
					</div>
				)}
			</div>

			<div className="flex items-center gap-6 text-sm">
				<div className="flex items-center gap-2">
					<span
						className="h-3 w-3 rounded-full"
						style={{ backgroundColor: typeColors.feature }}
					/>
					<span>Feature</span>
				</div>
				<div className="flex items-center gap-2">
					<span
						className="h-3 w-3 rounded-full"
						style={{ backgroundColor: typeColors.code }}
					/>
					<span>Code</span>
				</div>
				<div className="flex items-center gap-2">
					<span
						className="h-3 w-3 rounded-full"
						style={{ backgroundColor: typeColors.test }}
					/>
					<span>Test</span>
				</div>
				<div className="border-l pl-6 flex items-center gap-4">
					<div className="flex items-center gap-2">
						<div className="h-0.5 w-6" style={{ backgroundColor: "#9333ea" }} />
						<span>implements</span>
					</div>
					<div className="flex items-center gap-2">
						<div className="h-0.5 w-6" style={{ backgroundColor: "#22c55e" }} />
						<span>tests</span>
					</div>
					<div className="flex items-center gap-2">
						<div
							className="h-0.5 w-6 border-t-2 border-dashed"
							style={{ borderColor: "#f59e0b" }}
						/>
						<span>depends_on</span>
					</div>
				</div>
			</div>
		</div>
	);
}
