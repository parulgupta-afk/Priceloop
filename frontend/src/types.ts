export type ViewMode =
  | 'intro'
  | 'dashboard'
  | 'market-grid'
  | 'product-detail'
  | 'alerts'
  | 'competitors'
  | 'price-rules'
  | 'inventory'
  | 'reports'
  | 'settings';

export interface CompetitorListing {
  id: string;
  name: string;
  shortCode: string; // 'A', 'BB', 'W', 'T', etc.
  inStock: boolean;
  stockStatus: 'In Stock' | 'Low Stock' | 'Out of Stock';
  shipping: string; // 'Free', '+$5.99', 'Pickup Avail'
  price: number;
  deltaText?: string; // 'Match', '+$1.99', '+$7.00'
  isMatch?: boolean;
  lastUpdated: string;
}

export interface PricePoint {
  date: string;
  targetPrice: number;
  marketAvg: number;
  competitorMin: number;
}

export interface Product {
  id: string;
  name: string;
  subtitle: string;
  sku: string;
  category: string;
  imageUrl: string;
  targetPrice: number;
  marketAvg: number;
  priceDeltaAmount: number;
  priceDeltaPercent: number;
  priceChangeDirection: 'up' | 'down' | 'neutral';
  minPrice: number;
  maxPrice: number;
  marketPositionRank: number;
  marketPositionTotal: number;
  marketPositionLabel: string; // '#1 Cheapest', '#3 of 12', etc.
  aiSentiment: 'Bullish' | 'Bearish' | 'Neutral' | 'High Risk';
  aiInsight: {
    type: 'flash_sale' | 'optimal_price' | 'stable' | 'margin_warning' | 'stock_opportunity';
    title: string;
    description: string;
  };
  cogs: number;
  marginPercent: number;
  inventoryUnits: number;
  competitors: CompetitorListing[];
  priceHistory: PricePoint[];
  isBookmarked?: boolean;
}

export interface AlertItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  imageUrl: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
  timeAgo: string;
  type: 'price_drop' | 'margin_threshold' | 'stock_out';
  metricTitle: string;
  metricBadge: string;
  description: string;
  oldPrice?: number;
  newPrice?: number;
  competitorName?: string;
  resolved?: boolean;
}

export interface PriceRule {
  id: string;
  name: string;
  description: string;
  condition: string;
  action: string;
  targetCategory: string;
  status: 'active' | 'paused';
  appliedProductsCount: number;
  lastTriggered: string;
}

export interface MarketPositionStats {
  cheapestCount: number;
  cheapestPercent: number;
  midTierCount: number;
  midTierPercent: number;
  premiumCount: number;
  premiumPercent: number;
  totalProducts: number;
}
