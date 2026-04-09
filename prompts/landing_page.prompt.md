# Build a SaaS Landing Page

Build a modern, responsive landing page for a fictional productivity SaaS called "Flowdesk".

## Sections (top to bottom)
1. **Header** — sticky nav with logo, links (Features, Pricing, About), and "Get Started" CTA button
2. **Hero** — bold headline ("Focus on what matters"), subheading, two CTAs ("Start Free" + "See Demo"), abstract CSS/SVG geometric illustration on the right
3. **Features** — 3-column grid of 6 features with emoji icons, bold titles, short descriptions
4. **How It Works** — 3 numbered steps with a connecting dashed line between them
5. **Pricing** — 3 cards: Free ($0), Pro ($12/mo), Team ($29/mo). Pro card highlighted. Each card lists 5 features + CTA. Annual/monthly toggle showing 20% annual discount
6. **Testimonials** — 3 quote cards with CSS avatar (initials circle), name, role, company
7. **CTA Banner** — full-width dark section with headline and "Start Free" button
8. **Footer** — logo, 4 link columns, copyright

## Interactions
- Smooth scroll when clicking nav links
- Header gains drop-shadow after scrolling 50px (IntersectionObserver or scroll event)
- Pricing toggle: monthly / annual (JavaScript)
- Sections fade in on scroll (IntersectionObserver + CSS transition)

## Design
Deep navy hero (#0f172a). White content sections. Electric blue (#6366f1) accent.
Google Fonts: "Space Grotesk" headings, "Inter" body.
Modern SaaS look. No frameworks — pure HTML/CSS/JS.
Files: index.html, style.css, app.js
