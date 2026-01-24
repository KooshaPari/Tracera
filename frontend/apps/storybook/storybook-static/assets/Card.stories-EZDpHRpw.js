import { j as e } from "./index-Dj-uACAQ.js";
import { c as a, B as l, C as r, d as s, b as t } from "./Tooltip-GvgANCD2.js";
import "./iframe-BP6kYN29.js";
import "./preload-helper-PPVm8Dsz.js";
import "./index-DqgLOw3J.js";
const p = { title: "Components/Card", component: r, tags: ["autodocs"] },
	n = {
		render: () =>
			e.jsxs(r, {
				className: "w-[350px]",
				children: [
					e.jsx(t, { children: e.jsx(a, { children: "Card Title" }) }),
					e.jsx(s, {
						children: e.jsx("p", {
							children:
								"Card content goes here. This is a sample card component.",
						}),
					}),
				],
			}),
	},
	d = {
		render: () =>
			e.jsxs(r, {
				className: "w-[350px]",
				children: [
					e.jsx(t, { children: e.jsx(a, { children: "Project Card" }) }),
					e.jsxs(s, {
						children: [
							e.jsx("p", {
								className: "mb-4 text-muted-foreground",
								children: "A sample project with some description text.",
							}),
							e.jsxs("div", {
								className: "flex gap-2",
								children: [
									e.jsx(l, {
										variant: "outline",
										size: "sm",
										children: "Cancel",
									}),
									e.jsx(l, { size: "sm", children: "Open" }),
								],
							}),
						],
					}),
				],
			}),
	},
	o = {
		render: () =>
			e.jsxs("div", {
				className: "grid grid-cols-3 gap-4",
				children: [
					e.jsxs(r, {
						children: [
							e.jsx(t, {
								className: "pb-2",
								children: e.jsx(a, {
									className: "text-sm font-medium text-muted-foreground",
									children: "Total Items",
								}),
							}),
							e.jsx(s, {
								children: e.jsx("p", {
									className: "text-2xl font-bold",
									children: "1,234",
								}),
							}),
						],
					}),
					e.jsxs(r, {
						children: [
							e.jsx(t, {
								className: "pb-2",
								children: e.jsx(a, {
									className: "text-sm font-medium text-muted-foreground",
									children: "In Progress",
								}),
							}),
							e.jsx(s, {
								children: e.jsx("p", {
									className: "text-2xl font-bold text-blue-500",
									children: "42",
								}),
							}),
						],
					}),
					e.jsxs(r, {
						children: [
							e.jsx(t, {
								className: "pb-2",
								children: e.jsx(a, {
									className: "text-sm font-medium text-muted-foreground",
									children: "Completed",
								}),
							}),
							e.jsx(s, {
								children: e.jsx("p", {
									className: "text-2xl font-bold text-green-500",
									children: "892",
								}),
							}),
						],
					}),
				],
			}),
	};
n.parameters = {
	...n.parameters,
	docs: {
		...n.parameters?.docs,
		source: {
			originalSource: `{
  render: () => <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Card content goes here. This is a sample card component.</p>
      </CardContent>
    </Card>
}`,
			...n.parameters?.docs?.source,
		},
	},
};
d.parameters = {
	...d.parameters,
	docs: {
		...d.parameters?.docs,
		source: {
			originalSource: `{
  render: () => <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Project Card</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="mb-4 text-muted-foreground">A sample project with some description text.</p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Cancel
          </Button>
          <Button size="sm">Open</Button>
        </div>
      </CardContent>
    </Card>
}`,
			...d.parameters?.docs?.source,
		},
	},
};
o.parameters = {
	...o.parameters,
	docs: {
		...o.parameters?.docs,
		source: {
			originalSource: `{
  render: () => <div className="grid grid-cols-3 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Total Items</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">1,234</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">In Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-blue-500">42</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-green-500">892</p>
        </CardContent>
      </Card>
    </div>
}`,
			...o.parameters?.docs?.source,
		},
	},
};
const u = ["Default", "WithActions", "Stats"];
export {
	n as Default,
	o as Stats,
	d as WithActions,
	u as __namedExportsOrder,
	p as default,
};
