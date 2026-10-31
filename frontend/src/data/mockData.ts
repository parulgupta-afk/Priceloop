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
  midPackCount: 0,
  expensiveCount: 0,
  totalTracked: 0,
};
