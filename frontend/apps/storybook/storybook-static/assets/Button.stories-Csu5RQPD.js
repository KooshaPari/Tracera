import { j as r } from "./index-Dj-uACAQ.js";
import { B as e } from "./Tooltip-GvgANCD2.js";
import "./iframe-BP6kYN29.js";
import "./preload-helper-PPVm8Dsz.js";
import "./index-DqgLOw3J.js";
const f = {
		title: "Components/Button",
		component: e,
		tags: ["autodocs"],
		argTypes: {
			variant: {
				control: "select",
				options: [
					"default",
					"destructive",
					"outline",
					"secondary",
					"ghost",
					"link",
				],
			},
			size: { control: "select", options: ["default", "sm", "lg", "icon"] },
		},
		parameters: {
			design: {
				type: "figma",
				url: "https://www.figma.com/file/xxx/Design-System?node-id=123",
			},
			trace: { componentId: "comp-button-001", storyId: "story-button-001" },
		},
	},
	a = { args: { children: "Default", variant: "default" } },
	n = { args: { children: "Destructive", variant: "destructive" } },
	t = { args: { children: "Outline", variant: "outline" } },
	s = { args: { children: "Secondary", variant: "secondary" } },
	o = { args: { children: "Ghost", variant: "ghost" } },
	c = { args: { children: "Link", variant: "link" } },
	i = { args: { children: "Sm", size: "sm" } },
	d = { args: { children: "Lg", size: "lg" } },
	l = { args: { children: "Icon", size: "icon" } },
	u = {
		render: () =>
			r.jsxs("div", {
				className: "flex flex-wrap gap-4",
				children: [
					r.jsx(e, { variant: "default", children: "Default" }),
					r.jsx(e, { variant: "destructive", children: "Destructive" }),
					r.jsx(e, { variant: "outline", children: "Outline" }),
					r.jsx(e, { variant: "secondary", children: "Secondary" }),
					r.jsx(e, { variant: "ghost", children: "Ghost" }),
					r.jsx(e, { variant: "link", children: "Link" }),
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
n.parameters = {
	...n.parameters,
	docs: {
		...n.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Destructive',
    variant: 'destructive'
  }
}`,
			...n.parameters?.docs?.source,
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
    children: 'Outline',
    variant: 'outline'
  }
}`,
			...t.parameters?.docs?.source,
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
    children: 'Secondary',
    variant: 'secondary'
  }
}`,
			...s.parameters?.docs?.source,
		},
	},
};
o.parameters = {
	...o.parameters,
	docs: {
		...o.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Ghost',
    variant: 'ghost'
  }
}`,
			...o.parameters?.docs?.source,
		},
	},
};
c.parameters = {
	...c.parameters,
	docs: {
		...c.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Link',
    variant: 'link'
  }
}`,
			...c.parameters?.docs?.source,
		},
	},
};
i.parameters = {
	...i.parameters,
	docs: {
		...i.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Sm',
    size: 'sm'
  }
}`,
			...i.parameters?.docs?.source,
		},
	},
};
d.parameters = {
	...d.parameters,
	docs: {
		...d.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Lg',
    size: 'lg'
  }
}`,
			...d.parameters?.docs?.source,
		},
	},
};
l.parameters = {
	...l.parameters,
	docs: {
		...l.parameters?.docs,
		source: {
			originalSource: `{
  args: {
    children: 'Icon',
    size: 'icon'
  }
}`,
			...l.parameters?.docs?.source,
		},
	},
};
u.parameters = {
	...u.parameters,
	docs: {
		...u.parameters?.docs,
		source: {
			originalSource: `{
  render: () => <div className="flex flex-wrap gap-4">
      <Button variant="default">Default</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
    </div>
}`,
			...u.parameters?.docs?.source,
		},
	},
};
const S = [
	"Default",
	"Destructive",
	"Outline",
	"Secondary",
	"Ghost",
	"Link",
	"Sm",
	"Lg",
	"Icon",
	"AllVariants",
];
export {
	u as AllVariants,
	a as Default,
	n as Destructive,
	o as Ghost,
	l as Icon,
	d as Lg,
	c as Link,
	t as Outline,
	s as Secondary,
	i as Sm,
	S as __namedExportsOrder,
	f as default,
};
