/**
 * Offline UI placeholders only. Prefer live API data when authenticated.
 * Do not present these as real market prices in demos or README.
 */
import { Product, AlertItem, PriceRule, MarketPositionStats } from '../types';

export const INITIAL_PRODUCTS: Product[] = [];

export const INITIAL_ALERTS: AlertItem[] = [];

export const INITIAL_RULES: PriceRule[] = [];

export const MARKET_STATS: MarketPositionStats = {
  cheapestCount: 0,
  cheapestPercent: 0,
  midTierCount: 0,
  midTierPercent: 0,
  premiumCount: 0,
  premiumPercent: 0,
  totalProducts: 0,
};
