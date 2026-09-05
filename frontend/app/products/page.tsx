"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

type Product = {
  id: string;
  name: string;
  brand?: string;
  model?: string;
  created_at: string;
};

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  function getToken() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("priceloop_token");
  }

  async function load() {
    const token = getToken();
    if (!token) {
      setError("Please login first.");
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${API}/products`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Failed to load products");
      const data = await res.json();
      setProducts(data);
      setError("");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function createProduct(e: React.FormEvent) {
    e.preventDefault();
    const token = getToken();
    if (!token) return;
    const res = await fetch(`${API}/products`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name }),
    });
    if (res.ok) {
      setName("");
      load();
    } else {
      const err = await res.json();
      setError(err.detail || "Create failed");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h1>Products</h1>
      {error && <p style={{ color: "#f87171" }}>{error}</p>}

      <div className="card">
        <h2>Create product</h2>
        <form onSubmit={createProduct}>
          <label>Name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Sony WH-1000XM5"
            required
          />
          <button type="submit">Add</button>
        </form>
      </div>

      <div className="card">
        <h2>Your products</h2>
        {loading ? (
          <p className="muted">Loading…</p>
        ) : products.length === 0 ? (
          <p className="muted">No products yet.</p>
        ) : (
          <ul>
            {products.map((p) => (
              <li key={p.id} style={{ marginBottom: "0.5rem" }}>
                <strong>{p.name}</strong>
                {p.brand && <span className="muted"> · {p.brand}</span>}
                <div className="muted" style={{ fontSize: 12 }}>
                  {p.id}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
