# Kalshi NFL Markets Dashboard - UI Design Reference

## Visual Design System

### Color Palette

**Primary Colors:**
```css
Purple Gradient: #667eea → #764ba2
Green (Success): #10b981
Blue (Info): #3b82f6
Orange (Warning): #f59e0b
Red (Error): #ef4444
```

**Neutral Colors:**
```css
Background: #ffffff
Secondary Background: #f8f9fa
Text Primary: #262730
Text Secondary: #6b7280
Border: #e5e7eb
```

**Score Badge Colors:**
```css
Excellent (80+): #10b981 (green)
Good (70-79): #3b82f6 (blue)
Fair (60-69): #f59e0b (orange)
Poor (<60): #ef4444 (red)
```

### Typography

**Font Families:**
- System default (Streamlit): -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif

**Font Sizes:**
```css
Metric Value: 2.5rem (mobile: 1.8rem)
Page Title: 2rem
Section Header: 1.5rem
Body Text: 1rem
Caption: 0.9rem
Small: 0.8rem
```

**Font Weights:**
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

---

## Layout Components

### 1. Page Header

```
┌─────────────────────────────────────────────────────────────┐
│  🏈 Kalshi NFL Prediction Markets                           │
│  Modern dashboard for NFL prediction market analysis and... │
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Title: 2rem, bold
- Caption: 0.9rem, muted gray
- Padding: 1rem 0

### 2. Dashboard Metrics Row

```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│  Total   │   High   │   Avg    │  Total   │ Closing  │
│ Markets  │ Confid.  │   Edge   │  Volume  │  Today   │
│          │          │          │          │          │
│   581    │    127   │  +4.2%   │  $2.5M   │    12    │
│  ↑ 423   │  ↑ 21.8% │ Positive │ 89 liquid│  Urgent  │
└──────────┴──────────┴──────────┴──────────┴──────────┘
```

**Styling:**
- 5 equal columns (desktop)
- Stack vertically (mobile)
- Gradient background on hover
- Metric value: 2.5rem, bold
- Delta: 1rem, colored (green/red)

### 3. Filter Sidebar

```
┌─────────────────────────────────────┐
│  🔍 Filters & Search                │
├─────────────────────────────────────┤
│  🔎 Search                          │
│  [Search markets or players...]     │
│                                     │
│  🏈 Teams                            │
│  [ Select teams... ▼ ]              │
│                                     │
│  🎯 Bet Type                         │
│  ☑ Spread                           │
│  ☑ Total                            │
│  ☑ Moneyline                        │
│  ☑ Player Prop                      │
│  ☑ Parlay                           │
│                                     │
│  💯 Confidence Score                 │
│  ←───●──────────→ 60                │
│                                     │
│  📈 Edge Percentage                  │
│  ←───●──────────→ 0.0               │
│                                     │
│  ⏰ Timing                           │
│  [ All ▼ ]                          │
│                                     │
│  ⚠️ Risk Level                       │
│  ☑ Low                              │
│  ☑ Medium                           │
│  ☐ High                             │
│                                     │
├─────────────────────────────────────┤
│  [🔄 Refresh]  [🗑️ Clear]           │
└─────────────────────────────────────┘
```

**Styling:**
- Sidebar width: 300px
- Section spacing: 1.5rem
- Input backgrounds: white
- Borders: light gray (#e5e7eb)

### 4. Market Card (Expanded)

```
┌─────────────────────────────────────────────────────────────┐
│ 🔥 Will the Chiefs beat the Bills by more than 3 points?   │
├─────────────────────────────────────────────────────────────┤
│ Ticker: NFL-CHIEFS-001      │  Score: 85   │ Edge: +5.5%   │
│ Type: Spread                │  Risk: Low   │ Volume: $5K   │
│                             │              │ Closes: 2d    │
│                             │              │ Action: BUY   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  YES Price          │  NO Price                             │
│  65.0%              │  35.0%                                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  🤖 AI Analysis:                                            │
│  Strong value opportunity based on team performance and     │
│  recent trends. Market appears to be undervaluing Chiefs... │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ☐ Show Price History                                      │
│                                                             │
│  [⭐ Add to Watchlist] [📈 View on Kalshi] [🔔 Set Alert]  │
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Border-radius: 12px
- Border-left: 4px solid (gradient color)
- Box-shadow: 0 2px 8px rgba(0,0,0,0.08)
- Padding: 1.5rem
- Hover: lift effect (translateY(-2px))

### 5. Tab Navigation

```
┌───────────────────────────────────────────────────────────┐
│  🏈 All Markets  │  ⭐ Watchlist  │  ⚖️ Compare  │  📊 Ana│
└───────────────────────────────────────────────────────────┘
```

**Styling:**
- Active tab: purple gradient background
- Inactive: light gray background
- Border-radius: 8px 8px 0 0
- Font-weight: 600

### 6. Comparison Table

```
┌────────────┬───────────┬──────┬──────┬────────┬────────┐
│ Ticker     │ Market    │ Conf │ Edge │ Yes %  │ Volume │
├────────────┼───────────┼──────┼──────┼────────┼────────┤
│ NFL-001    │ Chiefs... │  85  │ 5.5  │  65.0  │  5000  │
│ NFL-002    │ Mahomes.. │  72  │ 3.2  │  58.0  │  3000  │
└────────────┴───────────┴──────┴──────┴────────┴────────┘
```

**Styling:**
- Full-width table
- Alternating row colors
- Hover: light purple background
- Header: bold, uppercase

### 7. Chart Container

```
┌─────────────────────────────────────────────────────────────┐
│  Price Movement - NFL-CHIEFS-001                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   100%  ┌────────────────────────────────────┐             │
│         │                          ╱          │             │
│    75%  │                    ╱─────           │ Yes Price   │
│         │               ╱────                 │             │
│    50%  ├──────────────●                      │             │
│         │         ╲                           │             │
│    25%  │          ╲───────                   │ No Price    │
│         │                  ╲─────────╲        │             │
│     0%  └────────────────────────────────────┘             │
│         Nov 1    Nov 3    Nov 5    Nov 7    Nov 9          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Height: 350-500px
- Template: plotly_white
- Hover mode: x unified
- Colors: Green (yes), Red (no)

### 8. Pagination Controls

```
┌─────────────────────────────────────────────────────────────┐
│  [⬅️ Previous]    Page 2 of 12    [Next ➡️]                 │
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Centered layout
- Button width: 150px
- Disabled state: gray, no hover

### 9. Analytics Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Market Analytics                                         │
├─────────────────────────────────────────────────────────────┤
│  [📈 Volume] [🎯 Confidence] [🔥 Heatmap] [💎 Edge]        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Volume Analysis                                    │   │
│  │                                                     │   │
│  │  [Bar chart showing top 10 markets by volume]      │   │
│  │                                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Total Volume: $2.5M  │  Avg: $4,300  │  High Vol: 89     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Styling:**
- Sub-tabs: pill style
- Chart height: 400-500px
- Metrics: 3-column layout

---

## Interactive States

### Button States

**Normal:**
```css
background: #667eea
color: white
border-radius: 8px
padding: 10px 20px
font-weight: 600
```

**Hover:**
```css
background: #5568d3
transform: translateY(-1px)
box-shadow: 0 4px 8px rgba(0,0,0,0.15)
```

**Active:**
```css
background: #4552b8
transform: translateY(0)
```

**Disabled:**
```css
background: #e5e7eb
color: #9ca3af
cursor: not-allowed
```

### Card States

**Normal:**
```css
box-shadow: 0 2px 8px rgba(0,0,0,0.08)
transform: translateY(0)
```

**Hover:**
```css
box-shadow: 0 4px 12px rgba(0,0,0,0.12)
transform: translateY(-2px)
transition: all 0.2s
```

### Input Focus

```css
border: 2px solid #667eea
box-shadow: 0 0 0 3px rgba(102,126,234,0.1)
outline: none
```

---

## Responsive Breakpoints

### Desktop (1200px+)

```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar  │              Main Content Area                  │
│  (300px)  │              (auto)                             │
│           │                                                 │
│  Filters  │  [5 metric cards in row]                       │
│           │                                                 │
│           │  [Tab navigation]                               │
│           │                                                 │
│           │  [Market cards grid - 2 columns]                │
│           │                                                 │
│           │  [Charts full width]                            │
└─────────────────────────────────────────────────────────────┘
```

### Tablet (768px - 1199px)

```
┌─────────────────────────────────────────────────────────────┐
│  [≡ Hamburger]  Main Content                                │
│                                                             │
│  [3 metric cards per row]                                  │
│                                                             │
│  [Tabs]                                                     │
│                                                             │
│  [Market cards - 1 column]                                  │
│                                                             │
│  [Charts full width]                                        │
└─────────────────────────────────────────────────────────────┘
```

### Mobile (< 768px)

```
┌──────────────────────────┐
│  [≡]  Page Title         │
├──────────────────────────┤
│  [Metric 1]              │
│  [Metric 2]              │
│  [Metric 3]              │
│  [Metric 4]              │
│  [Metric 5]              │
├──────────────────────────┤
│  [Tabs - scrollable]     │
├──────────────────────────┤
│  [Market Card]           │
│  [Market Card]           │
│  [Market Card]           │
├──────────────────────────┤
│  [Charts stacked]        │
└──────────────────────────┘
```

**Adjustments:**
- Font sizes: 20% smaller
- Padding: reduced to 0.75rem
- Touch targets: minimum 44px
- Swipe gestures: enabled

---

## Animation & Transitions

### Page Load

```css
Fade in: opacity 0 → 1 (300ms)
Slide up: translateY(10px) → 0 (300ms)
Stagger: 50ms delay between elements
```

### Filter Application

```css
Loading spinner: 200ms delay
Results fade: opacity 0.5 → 1 (200ms)
Count update: number animation (500ms)
```

### Chart Rendering

```css
Fade in: opacity 0 → 1 (400ms)
Draw animation: plotly default (750ms)
```

### Card Hover

```css
Lift: translateY(0) → translateY(-2px) (200ms ease-out)
Shadow: expand (200ms ease-out)
```

### Button Click

```css
Press: scale(1) → scale(0.98) (100ms)
Release: scale(0.98) → scale(1) (100ms)
```

---

## Icon System

**Emoji Icons Used:**

```
🏈 - NFL/Football
🔍 - Search/Filters
⭐ - Favorites/Watchlist
⚖️ - Comparison
📊 - Analytics/Charts
🎯 - Targeting/Accuracy
💯 - Confidence/Score
📈 - Trends/Growth
⏰ - Time/Schedule
⚠️ - Warning/Risk
🔔 - Alerts/Notifications
💰 - Money/Value
🤖 - AI/Automation
🔄 - Refresh/Reload
🗑️ - Delete/Remove
📥 - Download/Export
🔥 - Hot/Excellent
💎 - Premium/Quality
🎮 - Live/Active
```

**Icon Sizing:**
- Inline: 1.2em (scales with text)
- Button: 1.5em
- Header: 2em

---

## Chart Design Specifications

### 1. Odds Movement Chart

**Type:** Line chart (time series)

**Configuration:**
```python
colors = {
    'yes': '#10b981',  # Green
    'no': '#ef4444'    # Red
}
line_width = 3
marker_size = 6
height = 350px
template = 'plotly_white'
hover_mode = 'x unified'
```

### 2. Volume Chart

**Type:** Bar chart

**Configuration:**
```python
color = '#667eea'  # Purple
height = 400px
text_position = 'outside'
x_axis_rotation = -45
show_values = True
```

### 3. Confidence Distribution

**Type:** Histogram

**Configuration:**
```python
color = '#764ba2'  # Deep purple
bins = 20
opacity = 0.7
height = 350px
show_curve = True
```

### 4. Opportunity Heatmap

**Type:** Heatmap

**Configuration:**
```python
colorscale = 'RdYlGn'  # Red-Yellow-Green
show_values = True
value_format = '.1f%'
height = 500px
cell_annotations = True
```

### 5. Edge Scatter

**Type:** Scatter plot

**Configuration:**
```python
bubble_size = volume / 100
colorscale = 'Viridis'
height = 450px
hover_template = custom
marker_outline = white
```

---

## Accessibility Features

### Color Blindness Support

**Pattern Usage:**
- Icons + color (not color alone)
- Text labels on all chart elements
- Patterns in heatmaps (optional)

**Safe Color Combinations:**
- Green + Red: Also use ✓/✗ symbols
- Blue + Orange: High contrast
- Purple gradient: Single hue (safe)

### Screen Reader Support

**ARIA Labels:**
```html
<button aria-label="Add to watchlist">⭐</button>
<input aria-label="Search markets" placeholder="...">
<chart aria-label="Odds movement chart showing...">
```

### Keyboard Navigation

**Tab Order:**
1. Main navigation
2. Filter inputs (top to bottom)
3. Action buttons (left to right)
4. Market cards (top to bottom)
5. Pagination controls

**Shortcuts:**
- `Tab`: Next element
- `Shift+Tab`: Previous element
- `Enter`: Activate button/link
- `Space`: Toggle checkbox
- `Esc`: Close expanded card

---

## Mobile-Specific Design

### Touch Targets

**Minimum Sizes:**
- Buttons: 44×44 px
- Checkboxes: 32×32 px
- Links: 44 px height
- Slider handles: 48×48 px

### Gesture Support

**Swipe:**
- Left/Right: Navigate tabs
- Down: Refresh (pull-to-refresh)

**Tap:**
- Single: Select/Expand
- Double: Quick action (add to watchlist)

**Pinch:**
- Zoom charts (plotly handles)

### Mobile Optimization

**Image/Chart Loading:**
- Lazy load below fold
- Reduce quality on slow connections
- Show loading placeholders

**Network:**
- Cache aggressively
- Reduce API calls
- Compress responses

---

## Print Styles

```css
@media print {
    /* Hide navigation */
    .sidebar { display: none; }

    /* Single column layout */
    .columns { flex-direction: column; }

    /* Black & white friendly */
    .gradient { background: white; }

    /* Page breaks */
    .market-card { page-break-inside: avoid; }
}
```

---

## Dark Mode (Future)

**Colors:**
```css
Background: #1a202c
Surface: #2d3748
Text: #f7fafc
Primary: #667eea (unchanged)
```

**Implementation:**
```python
theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
if theme == "Dark":
    apply_dark_theme()
```

---

## Component Library

**Reusable Components:**

1. **MetricCard** - Dashboard metrics
2. **MarketCard** - Market display
3. **FilterSection** - Sidebar filter group
4. **ChartContainer** - Wrapper for plotly charts
5. **PaginationControls** - Navigation controls
6. **TableView** - Sortable data table
7. **BadgeLabel** - Score/status badges
8. **ButtonGroup** - Action button row

---

## Design Consistency Checklist

- [x] Consistent spacing (0.5rem, 1rem, 1.5rem, 2rem)
- [x] Consistent border-radius (8px, 12px)
- [x] Consistent colors (purple gradient theme)
- [x] Consistent font weights (400, 600, 700)
- [x] Consistent shadows (2px, 4px, 8px blur)
- [x] Consistent transitions (200ms, 300ms)
- [x] Consistent icon usage (emoji)
- [x] Consistent button styles
- [x] Consistent form inputs
- [x] Consistent chart styling

---

**Design Reference Created:** 2025-11-09
**Design System Version:** 1.0
**Framework:** Streamlit + Custom CSS
**Status:** Production Ready

---

This design reference ensures visual consistency across the entire dashboard and provides guidelines for future enhancements.
