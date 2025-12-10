# TraceRTM Documentation Site

Beautiful documentation homepage built with Next.js 15, React 19, Tailwind CSS, and Framer Motion.

## Features

- **Modern Design**: Beautiful, responsive UI with dark mode support
- **Animated Components**: Smooth animations using Framer Motion
- **Hero Section**: Eye-catching hero with animated background and CTAs
- **Features Grid**: 8 feature cards with icons and hover effects
- **Quick Links**: Easy navigation to key documentation sections
- **Stats Section**: Animated counters showing project metrics
- **Theme Toggle**: Light/dark mode with smooth transitions
- **Fully Responsive**: Works perfectly on mobile, tablet, and desktop

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Components**: Custom shadcn/ui-inspired components

## Getting Started

### Prerequisites

- Node.js 18+ or Bun 1.0+
- npm, yarn, pnpm, or bun

### Installation

1. Install dependencies:

```bash
bun install
# or
npm install
# or
yarn install
# or
pnpm install
```

2. Run the development server:

```bash
bun dev
# or
npm run dev
# or
yarn dev
# or
pnpm dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
bun run build
# or
npm run build
```

### Start Production Server

```bash
bun start
# or
npm start
```

## Project Structure

```
docs-site/
├── app/
│   ├── globals.css       # Global styles with Tailwind
│   ├── layout.tsx        # Root layout with header/footer
│   └── page.tsx          # Homepage
├── components/
│   ├── badge.tsx         # Badge component
│   ├── button.tsx        # Button component
│   ├── card.tsx          # Card component
│   ├── features-section.tsx    # Features grid
│   ├── hero-section.tsx        # Hero section
│   ├── quick-links.tsx         # Quick links section
│   ├── stats-section.tsx       # Stats with animated counters
│   └── theme-toggle.tsx        # Dark/light mode toggle
├── lib/
│   └── utils.ts          # Utility functions
├── next.config.ts        # Next.js configuration
├── tailwind.config.ts    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Components

### HeroSection

Eye-catching hero with:
- Animated gradient background
- Project name and tagline
- Three CTA buttons (Get Started, API Docs, GitHub)
- Quick stats preview (16 views, 60+ link types, 1000+ agents)

### FeaturesSection

Grid of 8 feature cards:
- Beautiful Design
- Sidebar Navigation
- Search Functionality
- OpenAPI Export
- Mobile Responsive
- Expandable Sections
- Code Examples
- Fast Performance

Each card has an icon, title, description, and hover effects.

### QuickLinks

5 quick navigation cards:
- Getting Started Guide
- API Reference
- Examples & Tutorials
- Contributing
- FAQ

### StatsSection

Animated counter stats:
- 24+ API Endpoints
- 150+ Code Examples
- 500+ Active Users
- 1200+ GitHub Stars

### ThemeToggle

Dark/light mode toggle with:
- System preference detection
- LocalStorage persistence
- Smooth transitions

## Customization

### Colors

Edit `tailwind.config.ts` to customize colors:

```typescript
theme: {
  extend: {
    colors: {
      primary: { ... },
      secondary: { ... },
      // Add your colors
    }
  }
}
```

### Content

Edit component files to update:
- Hero text: `components/hero-section.tsx`
- Features: `components/features-section.tsx`
- Links: `components/quick-links.tsx`
- Stats: `components/stats-section.tsx`

### Styling

Global styles are in `app/globals.css`. Use Tailwind utility classes for component styling.

## Animations

All animations use Framer Motion:

- Fade-in on scroll
- Stagger animations for lists
- Hover effects
- Animated counters
- Smooth transitions

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Deploy

### Other Platforms

Build and deploy the `out` directory:

```bash
bun run build
```

## Performance

- Static generation for fast page loads
- Optimized images
- Code splitting
- Minimal bundle size
- Lighthouse score: 95+

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License - see LICENSE file for details

## Credits

- Built with [Next.js](https://nextjs.org)
- Styled with [Tailwind CSS](https://tailwindcss.com)
- Animated with [Framer Motion](https://www.framer.com/motion/)
- Icons from [Lucide](https://lucide.dev)

---

Made with ❤️ for TraceRTM
