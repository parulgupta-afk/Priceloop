"use client";

import { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import { Headphones, BookOpen, Utensils, Wind, TrendingUp, TrendingDown, ShoppingBag, Bell, Activity } from "lucide-react";

// ---- Design tokens -------------------------------------------------------
// Cool "market board" palette. Icon badges give shopping-app warmth of
// texture without warming the color system itself. The stacking window
// section is the second orchestrated motion moment: each screen piles on
// the previous one as you scroll, like a deck of app windows.
const styleBlock = `
  :root {
    --paper: #EFEFEA;
    --paper-dim: #E4E3DC;
    --ink: #14171C;
    --ink-soft: #4B5157;
    --line: #D3D1C6;
    --board: #14171C;
    --board-cell: #1C2027;
    --flap: #F4F3EE;
    --rise: #B3402E;
    --drop: #276749;
    --brand: #1D3B53;
    --slate: #3B5BA9;
    --teal: #1F7A6C;
    --indigo: #4A4E9E;
    --steel: #55606B;
  }
  .font-serif-display { font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif; }
  .font-sans-ui { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, sans-serif; }
  .font-mono-board { font-family: "SF Mono", "Courier New", monospace; }

  .bg-paper { background-color: var(--paper); }
  .bg-paper-dim { background-color: var(--paper-dim); }
  .bg-board { background-color: var(--board); }
  .bg-cell { background-color: var(--board-cell); }
  .text-ink { color: var(--ink); }
  .text-ink-soft { color: var(--ink-soft); }
  .text-flap { color: var(--flap); }
  .text-rise { color: var(--rise); }
  .text-drop { color: var(--drop); }
  .text-brand { color: var(--brand); }
  .bg-brand { background-color: var(--brand); }
  .border-line { border-color: var(--line); }
  .border-cell { border-color: #2A2F38; }

  @keyframes flipRow {
    0%   { transform: rotateX(0deg); opacity: 1; }
    45%  { transform: rotateX(85deg); opacity: 0.4; }
    55%  { transform: rotateX(-85deg); opacity: 0.4; }
    100% { transform: rotateX(0deg); opacity: 1; }
  }
  .flip-cell {
    animation: flipRow 0.7s cubic-bezier(.4,0,.2,1);
    transform-origin: center;
    backface-visibility: hidden;
  }

  @keyframes marqueeScroll {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
  }
  .marquee-track {
    animation: marqueeScroll 26s linear infinite;
    width: max-content;
  }
  .marquee-track:hover {
    animation-play-state: paused;
  }
  .marquee-fade {
    -webkit-mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
    mask-image: linear-gradient(to right, transparent, black 8%, black 92%, transparent);
  }

  .nav-link {
    position: relative;
    padding-bottom: 2px;
  }
  .nav-link::after {
    content: "";
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 0%;
    height: 1px;
    background-color: var(--brand);
    transition: width 0.25s ease;
  }
  .nav-link:hover::after {
    width: 100%;
  }

  .cta-glow {
    transition: box-shadow 0.3s ease, transform 0.2s ease;
    box-shadow: 0 0 0 rgba(29, 59, 83, 0);
  }
  .cta-glow:hover {
    box-shadow: 0 6px 24px rgba(29, 59, 83, 0.35);
    transform: translateY(-1px);
  }

  @keyframes tickerScroll {
    from { transform: translateY(0); }
    to { transform: translateY(-50%); }
  }
  .ticker-track {
    animation: tickerScroll 14s linear infinite;
  }
  .ticker-fade {
    -webkit-mask-image: linear-gradient(to bottom, transparent, black 12%, black 88%, transparent);
    mask-image: linear-gradient(to bottom, transparent, black 12%, black 88%, transparent);
  }
`;

const PRODUCTS = [
  {
    name: "Sony WH-1000XM5",
    source: "3 sources",
    icon: Headphones,
    badge: "var(--slate)",
    sequence: [
      { price: "$348.00", delta: null },
      { price: "$329.00", delta: "down" },
      { price: "$339.00", delta: "up" },
      { price: "$319.00", delta: "down" },
    ],
  },
  {
    name: "Instant Pot Duo 6qt",
    source: "4 sources",
    icon: Utensils,
    badge: "var(--teal)",
    sequence: [
      { price: "$79.99", delta: null },
      { price: "$74.99", delta: "down" },
      { price: "$79.99", delta: "up" },
      { price: "$69.99", delta: "down" },
    ],
  },
  {
    name: "Kindle Paperwhite",
    source: "2 sources",
    icon: BookOpen,
    badge: "var(--indigo)",
    sequence: [
      { price: "$139.99", delta: null },
      { price: "$139.99", delta: null },
      { price: "$119.99", delta: "down" },
      { price: "$129.99", delta: "up" },
    ],
  },
  {
    name: "Dyson V8 Vacuum",
    source: "5 sources",
    icon: Wind,
    badge: "var(--steel)",
    sequence: [
      { price: "$279.00", delta: null },
      { price: "$299.00", delta: "up" },
      { price: "$249.00", delta: "down" },
      { price: "$259.00", delta: "up" },
    ],
  },
];

const CATEGORIES = [
  { label: "Electronics", icon: Headphones, color: "var(--slate)" },
  { label: "Kitchen", icon: Utensils, color: "var(--teal)" },
  { label: "Books", icon: BookOpen, color: "var(--indigo)" },
  { label: "Home", icon: Wind, color: "var(--steel)" },
];

const chartData = [
  { day: "Mon", price: 61 },
  { day: "Tue", price: 59.5 },
  { day: "Wed", price: 60 },
  { day: "Thu", price: 57 },
  { day: "Fri", price: 55.5 },
  { day: "Sat", price: 55.5 },
  { day: "Sun", price: 53 },
];

function IconBadge({ Icon, color, size = 40 }) {
  return (
    <div
      className="flex items-center justify-center rounded-full flex-shrink-0"
      style={{ width: size, height: size, backgroundColor: color }}
    >
      <Icon size={size * 0.5} color="#F4F3EE" strokeWidth={2} />
    </div>
  );
}

function DepartureBoard() {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 2600);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="bg-board border border-cell rounded-md p-5 w-full max-w-md font-mono-board">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-cell">
        <span className="text-flap text-xs tracking-wide opacity-90">live price board</span>
        <span className="text-flap text-xs opacity-50">updated just now</span>
      </div>
      <div className="space-y-1.5">
        {PRODUCTS.map((product, rowIdx) => {
          const state = product.sequence[(tick + rowIdx) % product.sequence.length];
          const Icon = product.icon;
          const DeltaIcon = state.delta === "up" ? TrendingUp : state.delta === "down" ? TrendingDown : null;
          return (
            <div key={product.name} className="flex items-center gap-3 bg-cell rounded-md px-3 py-2.5">
              <IconBadge Icon={Icon} color={product.badge} size={34} />
              <div className="flex flex-col flex-1 min-w-0">
                <span className="text-flap text-sm leading-tight truncate">{product.name}</span>
                <span className="text-flap text-xs opacity-40 leading-tight">{product.source}</span>
              </div>
              <div
                key={`${product.name}-${tick}`}
                className={
                  "flip-cell flex items-center gap-1 text-base tabular-nums " +
                  (state.delta === "down" ? "text-drop" : state.delta === "up" ? "text-rise" : "text-flap")
                }
              >
                {DeltaIcon && <DeltaIcon size={14} />}
                {state.price}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const FEATURES = [
  {
    title: "Track any product, anywhere it's sold",
    description: "Add one URL from Amazon, Walmart, or Target and Priceloop finds every other listing for the same item automatically.",
  },
  {
    title: "Know the moment a price moves",
    description: "Get an alert the moment a competitor drops price, restocks, or sells out -- not the next morning.",
  },
  {
    title: "Understand why, not just what",
    description: "Every alert comes with a plain-language explanation: a flash sale, a stockout, a seasonal dip.",
  },
  {
    title: "See where you stand",
    description: "A live board shows whether you're priced above, below, or right at the market for every product you track.",
  },
];

function FeatureMarquee() {
  const loop = [...FEATURES, ...FEATURES];
  return (
    <div className="marquee-fade overflow-hidden">
      <div className="flex gap-5 marquee-track">
        {loop.map((f, i) => (
          <div
            key={i}
            className="border border-line rounded-lg bg-white p-5 w-72 flex-shrink-0"
          >
            <h3 className="font-serif-display text-base text-ink mb-2 leading-snug">{f.title}</h3>
            <p className="text-sm text-ink-soft leading-relaxed">{f.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---- Count-up stats -------------------------------------------------------
// Numbers sit at zero until the section scrolls into view, then count up
// once -- a reveal tied to the user scrolling to it, not a looping effect.

function useInView(threshold = 0.4) {
  const [ref, setRef] = useState(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    if (!ref) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold }
    );
    observer.observe(ref);
    return () => observer.disconnect();
  }, [ref, threshold]);

  return [setRef, inView];
}

function StatCounter({ target, suffix = "", label, duration = 1200 }) {
  const [ref, inView] = useInView();
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const start = performance.now();
    let frame;
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, target, duration]);

  return (
    <div ref={ref} className="text-center">
      <p className="font-serif-display text-4xl text-ink tabular-nums">
        {value.toLocaleString()}
        {suffix}
      </p>
      <p className="text-sm text-ink-soft mt-1">{label}</p>
    </div>
  );
}

function StatsBand() {
  return (
    <section className="px-6 sm:px-10 py-14 max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-8 border-y border-line">
      <StatCounter target={12400} suffix="+" label="Products tracked" />
      <StatCounter target={480} suffix="+" label="Sources monitored" />
      <StatCounter target={99} suffix=".6%" label="Scrape success rate" />
    </section>
  );
}

// ---- Vertical live-activity ticker -----------------------------------------
// Same duplicate-and-loop trick as the horizontal feature marquee, but on
// the Y axis -- a different kind of motion so the page doesn't repeat itself.

const ACTIVITY_EVENTS = [
  { text: "Best Buy dropped Sony WH-1000XM5 to $329.00", tone: "drop" },
  { text: "Kindle Paperwhite back in stock at Target", tone: "neutral" },
  { text: "Dyson V8 up 8% across 2 sources", tone: "rise" },
  { text: "Instant Pot Duo matched across 4 marketplaces", tone: "neutral" },
  { text: "Amazon price steady on Sapiens for 12 days", tone: "neutral" },
  { text: "Walmart undercut market average by 4%", tone: "drop" },
];

function ActivityTicker() {
  const loop = [...ACTIVITY_EVENTS, ...ACTIVITY_EVENTS];
  return (
    <div className="ticker-fade h-64 overflow-hidden border border-line rounded-lg bg-white">
      <div className="ticker-track">
        {loop.map((event, i) => (
          <div
            key={i}
            className="flex items-center gap-3 px-4 py-3 border-b border-line last:border-b-0"
          >
            <span
              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
              style={{
                backgroundColor:
                  event.tone === "drop" ? "var(--drop)" : event.tone === "rise" ? "var(--rise)" : "var(--steel)",
              }}
            />
            <span className="text-sm text-ink-soft">{event.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActivityBand() {
  return (
    <section className="px-6 sm:px-10 py-16 max-w-2xl mx-auto">
      <div className="flex items-center gap-2 mb-4 justify-center">
        <span className="w-2 h-2 rounded-full bg-brand animate-pulse" />
        <p className="text-sm text-ink-soft">Live activity across every tracked source</p>
      </div>
      <ActivityTicker />
    </section>
  );
}
// Each window is position:sticky with a slightly increasing top offset and
// z-index. As the page scrolls, each new window slides up and piles on top
// of the one before it, which stays peeking out from behind -- a stack of
// app windows forming as you scroll, rather than one screen replacing another.

function WindowCard({ title, url, accent, children }) {
  return (
    <div className="border border-line rounded-lg overflow-hidden bg-white shadow-[0_12px_30px_-12px_rgba(20,23,28,0.35)]">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-line bg-paper-dim">
        <span className="w-2.5 h-2.5 rounded-full bg-line inline-block" />
        <span className="w-2.5 h-2.5 rounded-full bg-line inline-block" />
        <span className="w-2.5 h-2.5 rounded-full bg-line inline-block" />
        <span className="ml-3 text-xs text-ink-soft">{url}</span>
        <span className="ml-auto text-xs font-medium" style={{ color: accent }}>{title}</span>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}

const STACK_SCREENS = [
  {
    title: "Dashboard",
    url: "priceloop.app/dashboard",
    accent: "var(--slate)",
    content: (
      <div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          {[
            ["Tracked products", "128"],
            ["Active alerts", "6"],
            ["Avg. position", "Mid-tier"],
          ].map(([label, value]) => (
            <div key={label} className="border border-line rounded-md p-3">
              <p className="text-xs text-ink-soft mb-1">{label}</p>
              <p className="font-serif-display text-lg text-ink">{value}</p>
            </div>
          ))}
        </div>
        <div style={{ width: "100%", height: 120 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#4B5157" }} axisLine={false} tickLine={false} />
              <YAxis hide domain={["dataMin - 3", "dataMax + 3"]} />
              <Tooltip />
              <Line type="monotone" dataKey="price" stroke="#1D3B53" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    ),
  },
  {
    title: "Product detail",
    url: "priceloop.app/products/sony-wh-1000xm5",
    accent: "var(--teal)",
    content: (
      <div className="flex gap-6">
        <IconBadge Icon={Headphones} color="var(--slate)" size={56} />
        <div className="flex-1">
          <h4 className="font-serif-display text-xl text-ink mb-1">Sony WH-1000XM5</h4>
          <p className="text-xs text-ink-soft mb-3">Tracked across 3 sources</p>
          <div className="space-y-1.5 text-sm">
            <div className="flex justify-between"><span className="text-ink-soft">Amazon</span><span className="text-ink tabular-nums">$339.00</span></div>
            <div className="flex justify-between"><span className="text-ink-soft">Best Buy</span><span className="text-ink tabular-nums">$329.00</span></div>
            <div className="flex justify-between"><span className="text-ink-soft">Target</span><span className="text-ink tabular-nums">$349.00</span></div>
          </div>
        </div>
      </div>
    ),
  },
  {
    title: "Alerts",
    url: "priceloop.app/alerts",
    accent: "var(--indigo)",
    content: (
      <div className="space-y-3">
        {[
          { sev: "High", color: "var(--rise)", text: "Best Buy dropped Sony WH-1000XM5 by 6%" },
          { sev: "Info", color: "var(--steel)", text: "Kindle Paperwhite back in stock at Target" },
          { sev: "Warning", color: "var(--teal)", text: "Dyson V8 up 8% across 2 sources" },
        ].map((a) => (
          <div key={a.text} className="flex items-center gap-3 border-l-4 pl-3 py-1.5" style={{ borderColor: a.color }}>
            <Bell size={14} className="text-ink-soft" />
            <span className="text-sm text-ink">{a.text}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    title: "Scraper health",
    url: "priceloop.app/admin/scrapers",
    accent: "var(--steel)",
    content: (
      <div className="space-y-2">
        {[
          ["Amazon", "98.2%"],
          ["Best Buy", "94.7%"],
          ["Target", "91.3%"],
        ].map(([source, rate]) => (
          <div key={source} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-ink-soft"><Activity size={13} /> {source}</span>
            <span className="text-ink tabular-nums">{rate} success</span>
          </div>
        ))}
      </div>
    ),
  },
];

function StackingWindows() {
  return (
    <div className="relative max-w-2xl mx-auto">
      {STACK_SCREENS.map((screen, i) => (
        <div
          key={screen.title}
          style={{
            position: "sticky",
            top: `${96 + i * 28}px`,
            zIndex: i + 1,
            marginBottom: i === STACK_SCREENS.length - 1 ? 0 : "18vh",
          }}
        >
          <WindowCard title={screen.title} url={screen.url} accent={screen.accent}>
            {screen.content}
          </WindowCard>
        </div>
      ))}
    </div>
  );
}

export default function PriceloopLanding() {
  return (
    <div className="bg-paper min-h-screen font-sans-ui">
      <style>{styleBlock}</style>

      {/* Nav */}
      <nav className="flex items-center justify-between px-6 sm:px-10 py-5 border-b border-line sticky top-0 bg-paper z-50">
        <div className="flex items-center gap-2">
          <ShoppingBag size={20} className="text-brand" />
          <span className="font-serif-display text-xl text-ink">Priceloop</span>
        </div>
        <div className="hidden sm:flex items-center gap-8 text-sm text-ink-soft">
          <span className="nav-link">Product</span>
          <span className="nav-link">Pricing</span>
          <span className="nav-link">Docs</span>
        </div>
        <button className="cta-glow bg-brand text-flap text-sm px-4 py-2 rounded-full">
          Start tracking free
        </button>
      </nav>

      {/* Hero */}
      <section className="px-6 sm:px-10 py-16 sm:py-24 grid grid-cols-1 lg:grid-cols-2 gap-14 items-center max-w-6xl mx-auto">
        <div>
          <h1 className="font-serif-display text-4xl sm:text-5xl text-ink leading-tight mb-6 max-w-md">
            Watch every price move before your competitors do.
          </h1>
          <p className="text-ink-soft text-base leading-relaxed max-w-sm mb-8">
            Priceloop tracks prices across marketplaces, matches the same
            product wherever it's listed, and explains in plain language
            what changed and why.
          </p>
          <div className="flex items-center gap-6 mb-10">
            <button className="cta-glow bg-brand text-flap text-sm px-5 py-3 rounded-full">
              Start tracking free
            </button>
            <span className="text-sm text-ink-soft underline decoration-line underline-offset-4 cursor-pointer">
              See how it works
            </span>
          </div>
          <div className="flex items-center gap-3">
            {CATEGORIES.map((cat) => (
              <div key={cat.label} className="flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-full border border-line bg-paper-dim">
                <IconBadge Icon={cat.icon} color={cat.color} size={24} />
                <span className="text-xs text-ink-soft">{cat.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="flex justify-center lg:justify-end">
          <DepartureBoard />
        </div>
      </section>

      <StatsBand />

      {/* Feature marquee */}
      <section className="py-10">
        <FeatureMarquee />
      </section>

      <ActivityBand />

      {/* Scroll-stacking product screens */}
      <section className="px-6 sm:px-10 pt-16 pb-[40vh]">
        <p className="text-center text-sm text-ink-soft mb-10">Scroll to see it in action</p>
        <StackingWindows />
      </section>

      {/* Footer */}
      <footer className="border-t border-line">
        <div className="max-w-6xl mx-auto px-6 sm:px-10 py-12 grid grid-cols-2 sm:grid-cols-4 gap-8">
          <div className="col-span-2 sm:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <ShoppingBag size={18} className="text-brand" />
              <span className="font-serif-display text-lg text-ink">Priceloop</span>
            </div>
            <p className="text-xs text-ink-soft leading-relaxed max-w-[200px]">
              Price intelligence for sellers who don't want to check ten tabs a day.
            </p>
          </div>
          <div>
            <p className="text-xs text-ink-soft mb-3">Product</p>
            <div className="flex flex-col gap-2 text-sm text-ink">
              <span className="nav-link cursor-pointer w-fit">Dashboard</span>
              <span className="nav-link cursor-pointer w-fit">Alerts</span>
              <span className="nav-link cursor-pointer w-fit">Pricing</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-ink-soft mb-3">Company</p>
            <div className="flex flex-col gap-2 text-sm text-ink">
              <span className="nav-link cursor-pointer w-fit">About</span>
              <span className="nav-link cursor-pointer w-fit">Blog</span>
              <span className="nav-link cursor-pointer w-fit">Contact</span>
            </div>
          </div>
          <div>
            <p className="text-xs text-ink-soft mb-3">Legal</p>
            <div className="flex flex-col gap-2 text-sm text-ink">
              <span className="nav-link cursor-pointer w-fit">Privacy</span>
              <span className="nav-link cursor-pointer w-fit">Terms</span>
            </div>
          </div>
        </div>
        <div className="border-t border-line">
          <div className="max-w-6xl mx-auto px-6 sm:px-10 py-5 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-ink-soft">
            <span>&copy; {new Date().getFullYear()} Priceloop. All rights reserved.</span>
            <span>Made for sellers watching more than one marketplace.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
