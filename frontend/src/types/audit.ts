export type AuditStatus = "ok" | "error" | "timeout" | "unreachable";

export interface Headings {
  h1: number;
  h2: number;
  h3: number;
  h4: number;
  h5: number;
  h6: number;
}

export interface SeoMeta {
  title: string | null;
  description: string | null;
  title_length: number;
  description_length: number;
  has_canonical: boolean;
  has_open_graph: boolean;
  has_twitter_card: boolean;
  has_favicon: boolean;
  robots_meta: string | null;
}

export interface Links {
  internal: number;
  external: number;
  total: number;
}

export interface Images {
  total: number;
  without_alt: number;
}

export interface Performance {
  page_size_kb: number | null;
  approximate_word_count: number | null;
}

export interface SslInfo {
  valid: boolean;
  expires_in_days: number | null;
  issuer: string | null;
}

export interface AuditReport {
  url: string;
  final_url: string | null;
  timestamp: string;
  status: AuditStatus;
  status_code: number | null;
  response_time_ms: number | null;

  // ── Required flat fields per spec ──
  http_status: number;
  page_title: string | null;
  meta_description: string | null;
  h1_count: number;
  images_missing_alt_text: number;
  approximate_word_count: number;

  ssl: SslInfo;
  seo: SeoMeta;
  headings: Headings;
  links: Links;
  images: Images;
  performance: Performance;
  score: number;
  issues: string[];
  raw_headers: Record<string, string | number | string[]>;
}

export interface ApiError {
  detail: string;
  status: AuditStatus;
}
