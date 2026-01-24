import { j as r } from "./index-Dj-uACAQ.js";
import { A as e } from "./Tooltip-GvgANCD2.js";
import "./iframe-BP6kYN29.js";
import "./preload-helper-PPVm8Dsz.js";
import "./index-DqgLOw3J.js";
const p = {
		title: "Components/Alert",
		component: e,
		tags: ["autodocs"],
		argTypes: {
			variant: {
				control: "select",
				options: ["default", "destructive", "success", "warning"],
			},
		},
	},
	a = { args: { children: "Default", variant: "default" } },
	s = { args: { children: "Destructive", variant: "destructive" } },
	t = { args: { children: "Success", variant: "success" } },
	n = { args: { children: "Warning", variant: "warning" } },
	c = {
		render: () =>
			r.jsxs("div", {
				className: "flex flex-wrap gap-4",
				children: [
					r.jsx(e, { variant: "default", children: "Default" }),
					r.jsx(e, { variant: "destructive", children: "Destructive" }),
					r.jsx(e, { variant: "success", children: "Success" }),
					r.jsx(e, { variant: "warning", children: "Warning" }),
				],
			}),
	};
a.parameters = {
	...a.parameters,
	docs: {
		...a.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Default',
    variant: 'default'
  }
}`,
			...a.parameters?.docs?.source,
		},
	},
};
s.parameters = {
	...s.parameters,
	docs: {
		...s.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Destructive',
    variant: 'destructive'
  }
}`,
			...s.parameters?.docs?.source,
		},
	},
};
t.parameters = {
	...t.parameters,
	docs: {
		...t.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Success',
    variant: 'success'
  }
}`,
			...t.parameters?.docs?.source,
		},
	},
};
n.parameters = {
	...n.parameters,
	docs: {
		...n.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Warning',
    variant: 'warning'
  }
}`,
			...n.parameters?.docs?.source,
		},
	},
};
c.parameters = {
	...c.parameters,
	docs: {
		...c.parameters?.docs,
		source: {
			originalSource: `{
  render: () => <div className="flex flex-wrap gap-4">
      <Alert variant="default">Default</Alert>
      <Alert variant="destructive">Destructive</Alert>
      <Alert variant="success">Success</Alert>
      <Alert variant="warning">Warning</Alert>
    </div>
}`,
			...c.parameters?.docs?.source,
		},
	},
};
const m = ["Default", "Destructive", "Success", "Warning", "AllVariants"];
export {
	c as AllVariants,
	a as Default,
	s as Destructive,
	t as Success,
	n as Warning,
	m as __namedExportsOrder,
	p as default,
};
