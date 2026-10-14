// Small formatting helpers shared by the screens.

export function elapsed(ms: number): string {
  if (!Number.isFinite(ms) || ms < 0) ms = 0;
  const total = Math.floor(ms / 1000);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const mm = String(m).padStart(2, '0');
  const ss = String(s).padStart(2, '0');
  return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function tokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 10_000) return `${Math.round(n / 1000)}k`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

export function bytes(n: number): string {
  if (n >= 1024 * 1024) return `${(n / (1024 * 1024)).toFixed(1)} MB`;
  if (n >= 1024) return `${Math.round(n / 1024)} KB`;
  return `${n} B`;
}

export function ago(epochSeconds: number, now = Date.now()): string {
  if (!epochSeconds) return '-';
  const d = Math.max(0, now / 1000 - epochSeconds);
  if (d < 60) return 'just now';
  if (d < 3600) return `${Math.floor(d / 60)}m ago`;
  if (d < 86400) return `${Math.floor(d / 3600)}h ago`;
  if (d < 86400 * 30) return `${Math.floor(d / 86400)}d ago`;
  return new Date(epochSeconds * 1000).toISOString().slice(0, 10);
}

export function truncate(s: string, width: number): string {
  if (width <= 0) return '';
  if (s.length <= width) return s;
  if (width <= 3) return s.slice(0, width);
  return `${s.slice(0, width - 3)}...`;
}

export function truncateStart(s: string, width: number): string {
  if (s.length <= width) return s;
  if (width <= 3) return s.slice(-width);
  return `...${s.slice(-(width - 3))}`;
}

export function pad(s: string, width: number): string {
  const t = truncate(s, width);
  return t + ' '.repeat(Math.max(0, width - t.length));
}

export function padStart(s: string, width: number): string {
  const t = truncate(s, width);
  return ' '.repeat(Math.max(0, width - t.length)) + t;
}

export function slugify(name: string, now = new Date()): string {
  const base = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 32);
  return `${base || 'client'}-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

export function shortPath(p: string, home = process.env.HOME ?? ''): string {
  return home && p.startsWith(home) ? `~${p.slice(home.length)}` : p;
}

export function vmm(v: { blockers?: number | null; majors?: number | null; minors?: number | null } | null | undefined): string {
  if (!v) return '-';
  return `${v.blockers ?? 0}B/${v.majors ?? 0}M/${v.minors ?? 0}m`;
}

export function fmtEqi(e: unknown): string {
  if (e === null || e === undefined || e === '') return '-';
  const n = Number(e);
  if (!Number.isFinite(n)) return String(e);
  return Number.isInteger(n) ? String(n) : n.toFixed(n >= 100 ? 0 : 1);
}
