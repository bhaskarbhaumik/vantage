// Config browser/editor: tree view of the effective configuration; editing a leaf runs
// `vantage config set <dotted.key> <value>`.
import React, { useState } from 'react';
import { Box } from 'ink';
import TextInput from 'ink-text-input';
import { useAppCtx, useEngine, useKeys } from '../components/context.js';
import { ErrorPanel, Icon, Line, Loading, Panel, Txt, useIcon, useUi } from '../components/ui.js';
import type { Json } from '../lib/config.js';
import { truncate } from '../lib/format.js';

export interface TreeRow {
  path: string;
  key: string;
  depth: number;
  value: Json;
  leaf: boolean;
}

export function flattenTree(obj: Json, expanded: Set<string>, prefix = '', depth = 0): TreeRow[] {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return [];
  const rows: TreeRow[] = [];
  for (const [k, v] of Object.entries(obj)) {
    if (k.startsWith('$') || k.startsWith('_')) continue;
    const path = prefix ? `${prefix}.${k}` : k;
    const leaf = !(v && typeof v === 'object' && !Array.isArray(v));
    rows.push({ path, key: k, depth, value: v, leaf });
    if (!leaf && expanded.has(path)) rows.push(...flattenTree(v, expanded, path, depth + 1));
  }
  return rows;
}

export function renderValue(v: Json): string {
  if (v === null) return 'null';
  if (typeof v === 'string') return v;
  return JSON.stringify(v);
}

// What to send to `config set`: strings raw, everything else as JSON text.
export function editText(v: Json): string {
  return typeof v === 'string' ? v : JSON.stringify(v);
}

export const Config: React.FC = () => {
  const ctx = useAppCtx();
  const ui = useUi();
  const ic = useIcon();
  const cfg = useEngine(() => ctx.bridge.configShow());
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(['engine', 'auth', 'ui']));
  const [cursor, setCursor] = useState(0);
  const [edit, setEdit] = useState<{ path: string; value: string } | null>(null);
  const [saving, setSaving] = useState(false);

  // When the engine cannot answer, fall back to the local files (read-only).
  const fromEngine = Boolean(cfg.data);
  const data: Json = (cfg.data as Json) ?? (cfg.error ? ctx.localConfig : null);
  const rows = data ? flattenTree(data, expanded) : [];
  const cur = Math.min(cursor, Math.max(0, rows.length - 1));
  const row = rows[cur];
  const height = Math.max(6, ui.height - 12);
  const start = Math.max(0, Math.min(cur - Math.floor(height / 2), rows.length - height));

  const save = async (path: string, value: string, confirmed = false) => {
    if (path === 'auth.mode' && value.trim() === 'api-key' && !confirmed) {
      ctx.confirm(
        'Making api-key the default bills every future run per token to your provider account. ' +
          'Subscription mode runs on your Claude plan. Save auth.mode = api-key?',
        () => void save(path, value, true),
        'Billed per token',
      );
      return;
    }
    setSaving(true);
    const r = await ctx.bridge.configSet(path, value);
    setSaving(false);
    if (r.ok) {
      ctx.toast(`set ${path}`, 'ok');
      cfg.reload();
    } else {
      ctx.toast(r.error.split('\n')[0], 'err');
    }
  };

  const toggle = (p: string, open?: boolean) =>
    setExpanded((e) => {
      const n = new Set(e);
      const want = open ?? !n.has(p);
      if (want) n.add(p);
      else n.delete(p);
      return n;
    });

  useKeys((input, key) => {
    if (edit) {
      if (key.escape) setEdit(null);
      return true;
    }
    if (input === 'r') {
      cfg.reload();
      return true;
    }
    if (!row) return false;
    if (key.upArrow || input === 'k') {
      setCursor(Math.max(0, cur - 1));
      return true;
    }
    if (key.downArrow || input === 'j') {
      setCursor(Math.min(rows.length - 1, cur + 1));
      return true;
    }
    if (key.pageUp) {
      setCursor(Math.max(0, cur - height));
      return true;
    }
    if (key.pageDown) {
      setCursor(Math.min(rows.length - 1, cur + height));
      return true;
    }
    if (!row.leaf && (key.return || key.rightArrow || input === 'l' || input === ' ')) {
      toggle(row.path, key.rightArrow || input === 'l' ? true : undefined);
      return true;
    }
    if (key.leftArrow || input === 'h') {
      if (!row.leaf && expanded.has(row.path)) {
        toggle(row.path, false);
      } else {
        const parent = row.path.split('.').slice(0, -1).join('.');
        const pi = rows.findIndex((r) => r.path === parent);
        if (pi >= 0) setCursor(pi);
      }
      return true;
    }
    if (row.leaf && (key.return || input === 'e')) {
      if (!fromEngine) {
        ctx.toast('the engine is unavailable - config is read-only', 'warn');
        return true;
      }
      setEdit({ path: row.path, value: editText(row.value) });
      return true;
    }
    if (row.leaf && input === ' ' && typeof row.value === 'boolean' && fromEngine) {
      void save(row.path, String(!row.value));
      return true;
    }
    return false;
  });

  if (cfg.loading && !cfg.data) return <Loading label="reading the effective configuration" />;

  const valueW = Math.max(16, ui.width - 50);
  return (
    <Box flexDirection="column">
      {cfg.error ? (
        <ErrorPanel
          title="Engine config unavailable"
          message={cfg.error}
          hint="showing shipped defaults + ~/.config/vantage/default.json (read-only)  r retry"
        />
      ) : null}
      <Panel
        title={`Configuration ${fromEngine ? '(effective)' : '(local files)'}`}
        icon="config"
        focused
        right={saving ? <Txt tone="info">saving...</Txt> : <Txt dim>{rows.length} rows</Txt>}
      >
        {rows.slice(start, start + height).map((r, i) => {
          const sel = start + i === cur;
          return (
            <Line key={r.path} selected={sel}>
              <Txt>{'  '.repeat(r.depth)}</Txt>
              <Txt tone={r.leaf ? 'muted' : 'accent'}>
                {r.leaf ? ic('leaf') : ic(expanded.has(r.path) ? 'expand' : 'collapse')}{' '}
              </Txt>
              <Txt bold={sel || !r.leaf} tone={sel ? 'accent' : undefined}>
                {r.key}
              </Txt>
              {r.leaf ? (
                edit && edit.path === r.path ? (
                  <>
                    <Txt> = </Txt>
                    <TextInput
                      value={edit.value}
                      onChange={(v) => setEdit({ path: r.path, value: v })}
                      onSubmit={(v) => {
                        setEdit(null);
                        void save(r.path, v);
                      }}
                      focus
                    />
                  </>
                ) : (
                  <Txt tone={typeof r.value === 'boolean' ? (r.value ? 'ok' : 'warn') : r.value === null ? 'muted' : 'info'}>
                    {' = '}
                    {truncate(renderValue(r.value), valueW)}
                  </Txt>
                )
              ) : (
                <Txt dim> {'{'}{Object.keys(r.value as object).length}{'}'}</Txt>
              )}
            </Line>
          );
        })}
        {row ? (
          <Box marginTop={1}>
            <Icon name="tree" tone="muted" />
            <Txt dim>{row.path}</Txt>
          </Box>
        ) : null}
      </Panel>
    </Box>
  );
};

export const CONFIG_KEYS: [string, string][] = [
  ['up/down', 'move'],
  ['right/enter', 'expand a section'],
  ['left', 'collapse / go to parent'],
  ['enter / e', 'edit a value (vantage config set)'],
  ['space', 'toggle a boolean'],
  ['esc', 'cancel an edit'],
  ['r', 'reload'],
];
