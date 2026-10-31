/**
 * Intelligence / analyst / forecast API (PriceLoop 2.0).
 */
import { api } from './client';

export async function getProductSummary(productId: string, days = 30) {
  return api.get<Record<string, unknown>>(`/products/${productId}/summary?days=${days}`);
}

export async function getProductForecast(productId: string, horizonDays = 7) {
  return api.get<Record<string, unknown>>(
    `/products/${productId}/forecast?horizon_days=${horizonDays}`,
  );
}

export async function getProductAnomalies(productId: string, days = 60) {
  return api.get<Record<string, unknown>>(`/products/${productId}/anomalies?days=${days}`);
}

export async function askAnalyst(query: string) {
  return api.post<{
    query: string;
    answer: string;
    evidence: Record<string, unknown>;
    tool_trace: unknown[];
    limitations: string[];
  }>(`/ai/query`, { query });
}

export async function evaluateAlertsDeduped() {
  return api.post<Record<string, unknown>>(`/alerts/evaluate-deduped`, {});
}

export async function listScrapeJobs(limit = 50) {
  return api.get<unknown[]>(`/scrape-jobs?limit=${limit}`);
}
