# TraceRTM Documentation Site - Setup Instructions

## Quick Start

The documentation homepage is now complete! Here's how to get started:

### 1. Start Development Server

```bash
cd docs-site
bun dev
```

The site will be available at http://localhost:3000

### 2. View the Homepage

Open your browser and navigate to http://localhost:3000 to see:

- **Hero Section**: Animated background with project title, tagline, and CTA buttons
- **Features Section**: 8 feature cards with icons and hover effects
- **Quick Links Section**: 5 navigation cards to key documentation areas
- **Stats Section**: Animated counters showing project metrics

### 3. Toggle Dark/Light Mode

Click the sun/moon icon in the top-right header to switch between light and dark themes.

## What's Included

### Components Created

1. **hero-section.tsx** - Hero with animated background
   - Gradient animated background
   - Pulsing orbs
   - Grid pattern overlay
   - Version badge
   - 3 CTA buttons
   - Quick stats preview

2. **features-section.tsx** - Features grid
   - 8 feature cards
   - Lucide icons
   - Hover animations
   - Stagger entrance

3. **quick-links.tsx** - Quick navigation
   - 5 link cards
   - Arrow hover effects
   - Colored accents

4. **stats-section.tsx** - Animated stats
   - 4 stat cards
   - Animated counters using Framer Motion
   - Spring animations

5. **theme-toggle.tsx** - Dark/light mode
   - System preference detection
   - LocalStorage persistence
   - Smooth transitions

### Base Components

- **button.tsx** - Styled button with variants
- **card.tsx** - Card container with header/content/footer
- **badge.tsx** - Badge component for labels

### Layout

- **layout.tsx** - Root layout with header and footer
  - Sticky header with logo and navigation
  - Theme toggle in header
  - Footer with links
  
- **page.tsx** - Homepage integrating all sections

## Customization Guide

### Update Hero Content

Edit `components/hero-section.tsx`:

```typescript
// Change title
<h1>Your Title</h1>

// Update tagline
<p>Your tagline</p>

// Modify stats
<div className="text-3xl font-bold">Your Number</div>
<div className="text-sm">Your Label</div>
```

### Update Features

Edit `components/features-section.tsx`:

```typescript
const features = [
  {
    icon: YourIcon,
    title: "Feature Title",
    description: "Feature description",
    color: "text-blue-600",
    bgColor: "bg-blue-100"
  },
  // Add more features
]
```

### Update Quick Links

Edit `components/quick-links.tsx`:

```typescript
const links = [
  {
    icon: YourIcon,
    title: "Link Title",
    description: "Link description",
    href: "/your-path",
    color: "text-blue-600",
    bgColor: "bg-blue-50"
  },
  // Add more links
]
```

### Update Stats

Edit `components/stats-section.tsx`:

```typescript
const stats = [
  {
    icon: YourIcon,
    value: 100,
    label: "Your Metric",
    suffix: "+",
    color: "text-blue-600",
    bgColor: "bg-blue-100"
  },
  // Add more stats
]
```

### Change Colors

Edit `tailwind.config.ts` to customize the color scheme:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        DEFAULT: 'hsl(var(--primary))',
        foreground: 'hsl(var(--primary-foreground))',
      },
      // Customize other colors
    }
  }
}
```

Then update CSS variables in `app/globals.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%; /* Blue */
  /* Change to your color in HSL format */
}
```

## Build for Production

```bash
# Build
bun run build

# Preview production build
bun start
```

## Deploy to Vercel

1. Push to GitHub
2. Import in Vercel
3. Deploy (auto-detected as Next.js)

## Tips

### Performance
- All components use Framer Motion for smooth animations
- Images should go in `public/` directory
- Use Next.js Image component for optimization

### Accessibility
- All interactive elements have proper ARIA labels
- Theme toggle includes screen reader text
- Semantic HTML structure

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Test on different screen sizes

## Troubleshooting

### Port Already in Use

```bash
# Use different port
bun dev --port 3001
```

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next
bun run build
```

### Type Errors

```bash
# Check TypeScript
bun run typecheck
```

## Next Steps

1. Add more pages (Getting Started, API Reference, etc.)
2. Implement search functionality
3. Add code syntax highlighting
4. Create documentation content
5. Add MDX support for content

## Support

For issues or questions:
- Check the README.md
- Review Next.js documentation
- Check Framer Motion docs for animation help

---

Happy coding!
