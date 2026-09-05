import { api } from './client';

export interface BackendListing {
  id: string;
  product_id: string;
  source_id: string;
  external_url: string;
  external_id: string | null;
  title: string | null;
  current_price: number | string | null;
  currency: string;
  availability: string;
  match_confidence: number | null;
  last_scraped_at: string | null;
  is_active: boolean;
  created_at: string;
}

export interface BackendProduct {
  id: string;
  user_id: string;
  name: string;
  brand: string | null;
  model: string | null;
  category: string | null;
  sku: string | null;
  gtin: string | null;
  description: string | null;
  image_url: string | null;
  attributes: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  listings: BackendListing[];
}

export interface BackendPriceObservation {
  id: string;
  listing_id: string;
  price: number | string;
  currency: string;
  availability: string;
  scraped_at: string;
}

export async function listProducts(skip = 0, limit = 50): Promise<BackendProduct[]> {
  return api.get<BackendProduct[]>(`/products?skip=${skip}&limit=${limit}`);
}

export async function getProduct(id: string): Promise<BackendProduct> {
  return api.get<BackendProduct>(`/products/${id}`);
}

export async function createProduct(payload: {
  name: string;
  brand?: string;
  model?: string;
  category?: string;
  sku?: string;
  description?: string;
  image_url?: string;
}): Promise<BackendProduct> {
  return api.post<BackendProduct>('/products', payload);
}

export async function addListing(
  productId: string,
  payload: { source_name: string; external_url: string; external_id?: string }
): Promise<BackendListing> {
  return api.post<BackendListing>(`/products/${productId}/listings`, payload);
}

export async function getProductPrices(
  productId: string,
  limit = 100
): Promise<BackendPriceObservation[]> {
  return api.get<BackendPriceObservation[]>(
    `/products/${productId}/prices?limit=${limit}`
  );
}

export async function triggerScrape(listingId: string): Promise<BackendPriceObservation> {
  return api.post<BackendPriceObservation>(`/listings/${listingId}/scrape`);
}

export async function getProductAnalytics(productId: string, days = 30): Promise<Record<string, unknown>> {
  return api.get(`/products/${productId}/analytics?days=${days}`);
}

export async function getProductInsights(productId: string): Promise<Record<string, unknown>> {
  try {
    return await api.get(`/products/${productId}/insights`);
  } catch {
    return {};
  }
}
