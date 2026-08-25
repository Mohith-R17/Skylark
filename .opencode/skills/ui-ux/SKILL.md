# ui-ux/SKILL.md

## Premium Enterprise BI Interface Standards

### Typography
- Use system font stack with proper scaling: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- Headings: Scale 2xl (1.5rem) to 6xl (3rem) with tracking-tight
- Body text: Base 1rem, leading-relaxed, max width 768px for long-form content
- Monospace/code: Menlo, Consolas, "Liberation Mono", monospace at base 0.875rem

### Spacing & Layout
- Scale: 0, 4, 8, 12, 16, 24, 32, 40, 48
- Container max-width: 1280px with 1rem padding on sides, centered
- Section gaps: 6-8 rem between major sections
- Card padding: 1.5rem minimum, 2rem for premium sections

### Color System (Dark Mode Optimized)
- Background: #0a0a0f (near-black) surface, #1e1e2a for cards
- Primary: #00d4aa (emerald), secondary: #6366f1 (indigo)
- Text: #f8fafc (light), #1e293b (readable on light)
- Borders: #334155 muted, focus ring: #00d4aa

### Components
- **Cards**: Elevated with subtle shadow (0 1px 2px 0 rgba(0,0,0,0.1)), rounded lg (0.5rem), no glassmorphism
- **Buttons**: Solid primary, subtle hover, no gradients. Text buttons with underline on hover
- **Inputs**: Bordered, focused state with primary ring, error state with red accent
- **Selects/Inputs**: shadcn/ui primitives with proper labels

### Charts (Recharts)
- No excessive gradients or glassmorphism on charts
- Clean lines, subtle gridlines (#e2e8f0), clear legend
- Data points with small dots, not overwhelming
- Responsive: chart resizes with container, min-width 320px

### Tables
- Zebra striping: alternating row bg #1e293b / #0d1117
- Hover state: subtle #0f172a highlight
- Sortable arrows: #64748b muted
- Text truncation with ellipsis for long values

### Responsive Design
- Mobile-first: stack vertically below 640px
- Table horizontal scroll below 768px
- Chart width: 100% on mobile, adjustable on desktop
- Typography scales: heading sizes reduce on mobile

### Accessibility
- Contrast ratio: minimum 4.5:1, preferably 7:1
- Focus visible: primary color focus ring, not outline none
- Keyboard navigation: tab through all interactive elements
- Alt text required for all data visualization icons/images
- ARIA labels on dynamic content, live regions for loading states

### Loading/Empty/Error States
- **Loading**: Skeleton screens matching content layout, spinners with motion
- **Empty**: Illustration + descriptive text + suggested actions
- **Error**: Clear message + retry button + optional details collapse

### Animations
- Duration: 150-300ms for most transitions
- Easing: cubic-bezier(0.4, 0, 0.2, 1) for most
- Subtle only: hover color shifts, focus reveal, card lift on hover
- No auto-running animations on page load

### Conversational UX
- Progress indicators for data queries
- Inline error explanations (not modals unless critical)
- Confirmation for destructive actions
- Empty states with "What would you like to explore next?"
- Tool tips on hover for chart axes and table headers