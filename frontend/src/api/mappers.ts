/**
 * Map backend Product + listings + price history + analytics
 * into the rich UI Product shape used by the exact design.
 */
import type { Product, CompetitorListing, PricePoint, AlertItem } from '../types';
import type { BackendProduct, BackendPriceObservation } from './products';

function num(v: number | string | null | undefined, fallback = 0): number {
  if (v === null || v === undefined) return fallback;
  const n = typeof v === 'string' ? parseFloat(v) : v;
  return Number.isFinite(n) ? n : fallback;
}

function sourceShortCode(name: string): string {
  const n = name.toLowerCase();
  if (n.includes('amazon')) return 'A';
  if (n.includes('best')) return 'BB';
  if (n.includes('walmart')) return 'W';
  if (n.includes('target')) return 'T';
  if (n.includes('flipkart')) return 'FK';
  if (n.includes('demo')) return 'D';
  return name.slice(0, 2).toUpperCase();
}

function availabilityToStatus(
  a: string
): 'In Stock' | 'Low Stock' | 'Out of Stock' {
  const s = (a || '').toUpperCase();
  if (s.includes('OUT') || s === 'UNAVAILABLE') return 'Out of Stock';
  if (s.includes('LOW')) return 'Low Stock';
  return 'In Stock';
}

function relativeTime(iso: string | null): string {
  if (!iso) return '—';
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return '—';
  const diff = Date.now() - t;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins} mins ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
}

export function mapBackendProductToUI(
  bp: BackendProduct,
  prices: BackendPriceObservation[] = [],
  analytics: Record<string, unknown> = {}
): Product {
  const listings = bp.listings || [];
  const pricesNum = listings
    .map((l) => num(l.current_price, NaN))
    .filter((p) => Number.isFinite(p));

  const currentFromAnalytics = num(analytics.current_price as any, NaN);
  const minFromAnalytics = num(analytics.min_price as any, NaN);
  const maxFromAnalytics = num(analytics.max_price as any, NaN);
  const avgFromAnalytics = num(analytics.avg_price as any, NaN);
  const changePct = num(analytics.price_change_pct as any, NaN);

  const targetPrice =
    pricesNum.length > 0
      ? Math.min(...pricesNum)
      : Number.isFinite(currentFromAnalytics)
      ? currentFromAnalytics
      : 0;

  const marketAvg =
    Number.isFinite(avgFromAnalytics) && avgFromAnalytics > 0
      ? avgFromAnalytics
      : pricesNum.length
      ? pricesNum.reduce((a, b) => a + b, 0) / pricesNum.length
      : targetPrice;

  const minPrice = Number.isFinite(minFromAnalytics)
    ? minFromAnalytics
    : pricesNum.length
    ? Math.min(...pricesNum)
    : targetPrice;
  const maxPrice = Number.isFinite(maxFromAnalytics)
    ? maxFromAnalytics
    : pricesNum.length
    ? Math.max(...pricesNum)
    : targetPrice;

  const deltaAmount = Number((targetPrice - marketAvg).toFixed(2));
  const deltaPercent =
    marketAvg > 0
      ? Number((((targetPrice - marketAvg) / marketAvg) * 100).toFixed(1))
      : 0;

  const competitors: CompetitorListing[] = listings.map((l, idx) => {
    const price = num(l.current_price, 0);
    const delta = price - targetPrice;
    const isMatch = Math.abs(delta) < 0.5;
    return {
      id: l.id,
      name: l.title || `Source ${idx + 1}`,
      shortCode: sourceShortCode(
        (l as any).source_name || l.title || `S${idx + 1}`
      ),
      inStock: availabilityToStatus(l.availability) !== 'Out of Stock',
      stockStatus: availabilityToStatus(l.availability),
      shipping: '—',
      price,
      deltaText: isMatch ? 'Match' : delta > 0 ? `+$${delta.toFixed(2)}` : `-$${Math.abs(delta).toFixed(2)}`,
      isMatch,
      lastUpdated: relativeTime(l.last_scraped_at),
    };
  });

  // Price history from observations
  const sorted = [...prices].sort(
    (a, b) => new Date(a.scraped_at).getTime() - new Date(b.scraped_at).getTime()
  );
  const priceHistory: PricePoint[] = sorted.slice(-30).map((o) => {
    const p = num(o.price, 0);
    return {
      date: new Date(o.scraped_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
      targetPrice: p,
      marketAvg: marketAvg || p,
      competitorMin: minPrice || p,
    };
  });

  // If no history, create a single point so charts don't break
  if (priceHistory.length === 0 && targetPrice > 0) {
    priceHistory.push({
      date: 'Now',
      targetPrice,
      marketAvg: marketAvg || targetPrice,
      competitorMin: minPrice || targetPrice,
    });
  }

  const rank = competitors.length
    ? competitors.filter((c) => c.price < targetPrice - 0.01).length + 1
    : 1;
  const total = Math.max(competitors.length, 1);

  let aiSentiment: Product['aiSentiment'] = 'Neutral';
  let insightType: Product['aiInsight']['type'] = 'stable';
  let insightTitle = 'Market data loaded';
  let insightDesc =
    analytics.message && typeof analytics.message === 'string'
      ? (analytics.message as string)
      : `Live data from backend. ${prices.length} price observations.`;

  if (Number.isFinite(changePct)) {
    if (changePct <= -5) {
      aiSentiment = 'Bullish';
      insightType = 'optimal_price';
      insightTitle = 'Price dropped';
      insightDesc = `Price is down ${Math.abs(changePct).toFixed(1)}% in the selected window.`;
    } else if (changePct >= 5) {
      aiSentiment = 'Bearish';
      insightType = 'margin_warning';
      insightTitle = 'Price increased';
      insightDesc = `Price is up ${changePct.toFixed(1)}% — review margin.`;
    }
  }

  const cogs = num((bp.attributes as any)?.cogs, targetPrice * 0.7);
  const marginPercent =
    targetPrice > 0 ? Number((((targetPrice - cogs) / targetPrice) * 100).toFixed(1)) : 0;

  return {
    id: bp.id,
    name: bp.name,
    subtitle: bp.description || [bp.brand, bp.model].filter(Boolean).join(' ') || bp.category || '',
    sku: bp.sku || bp.id.slice(0, 8).toUpperCase(),
    category: bp.category || 'General',
    imageUrl:
      bp.image_url ||
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
    targetPrice,
    marketAvg,
    priceDeltaAmount: deltaAmount,
    priceDeltaPercent: deltaPercent,
    priceChangeDirection:
      deltaAmount < -0.5 ? 'down' : deltaAmount > 0.5 ? 'up' : 'neutral',
    minPrice,
    maxPrice,
    marketPositionRank: rank,
    marketPositionTotal: total,
    marketPositionLabel:
      rank === 1 ? '#1 Cheapest' : `#${rank} of ${total}`,
    aiSentiment,
    aiInsight: {
      type: insightType,
      title: insightTitle,
      description: insightDesc,
    },
    cogs,
    marginPercent,
    inventoryUnits: num((bp.attributes as any)?.inventory, 0),
    competitors,
    priceHistory,
    isBookmarked: false,
  };
}

export function mapAnalyticsToMarketStats(
  products: Product[]
): {
  cheapestCount: number;
  cheapestPercent: number;
  midTierCount: number;
  midTierPercent: number;
  premiumCount: number;
  premiumPercent: number;
  totalProducts: number;
} {
  const total = products.length || 1;
  let cheapest = 0;
  let mid = 0;
  let premium = 0;
  for (const p of products) {
    if (p.marketPositionRank === 1) cheapest++;
    else if (p.priceDeltaPercent > 5) premium++;
    else mid++;
  }
  return {
    cheapestCount: cheapest,
    cheapestPercent: Math.round((cheapest / total) * 100),
    midTierCount: mid,
    midTierPercent: Math.round((mid / total) * 100),
    premiumCount: premium,
    premiumPercent: Math.round((premium / total) * 100),
    totalProducts: products.length,
  };
}

/** Build simple AlertItems from products that show large price moves */
export function deriveAlertsFromProducts(products: Product[]): AlertItem[] {
  const alerts: AlertItem[] = [];
  for (const p of products) {
    if (Math.abs(p.priceDeltaPercent) >= 3) {
      alerts.push({
        id: `alert-${p.id}`,
        productId: p.id,
        productName: p.name,
        sku: p.sku,
        imageUrl: p.imageUrl,
        severity:
          Math.abs(p.priceDeltaPercent) >= 10
            ? 'critical'
            : Math.abs(p.priceDeltaPercent) >= 5
            ? 'warning'
            : 'info',
        timestamp: new Date().toISOString(),
        timeAgo: 'just now',
        type: p.priceDeltaPercent < 0 ? 'price_drop' : 'margin_threshold',
        metricTitle:
          p.priceDeltaPercent < 0 ? 'Competitor undercut' : 'Price above market',
        metricBadge: `${p.priceDeltaPercent > 0 ? '+' : ''}${p.priceDeltaPercent}%`,
        description: p.aiInsight.description,
        oldPrice: p.marketAvg,
        newPrice: p.targetPrice,
        resolved: false,
      });
    }
  }
  return alerts;
}
