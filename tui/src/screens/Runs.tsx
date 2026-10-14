// Runs browser: sortable, filterable list of past runs, and one run's detail view.
import React, { useState } from 'react';
import { Box } from 'ink';
import TextInput from 'ink-text-input';
import { useAppCtx, useEngine, useKeys } from '../components/context.js';
import { ErrorPanel, Field, Icon, Line, Loading, Panel, Txt, useIcon, useUi } from '../components/ui.js';
import type { RunInfo } from '../lib/engine.js';
import { ago, fmtEqi, pad, shortPath, truncate, vmm } from '../lib/format.js';
import { copyText, openPath } from '../lib/system.js';
import { bandTone } from '../lib/theme.js';

export const SORTS = ['modified', 'slug', 'client', 'confidence', 'eqi'] as const;
export type SortKey = (typeof SORTS)[number];

const BAND_RANK: Record<string, number> = { insufficient: 0, thin: 1, low: 1, moderate: 2, medium: 2, adequate: 2, high: 3, strong: 4 };

function bandRank(r: RunInfo): number {
  const b = (r.verification?.overall_confidence ?? '').toLowerCase();
  return b ? BAND_RANK[b.split(/\s/)[0]] ?? 2 : -1;
}

function eqiOf(r: RunInfo): number {
  const e = Number(r.verification?.eqi);
  return Number.isFinite(e) ? e : -1;
}

export function sortRuns(runs: RunInfo[], key: SortKey, desc: boolean): RunInfo[] {
  const cmp = (a: RunInfo, b: RunInfo): number => {
    switch (key) {
      case 'modified':
        return (a.mtime ?? 0) - (b.mtime ?? 0);
      case 'slug':
        return a.slug.localeCompare(b.slug);
      case 'client':
        return (a.client ?? '').localeCompare(b.client ?? '');
      case 'confidence':
        return bandRank(a) - bandRank(b);
      case 'eqi':
        return eqiOf(a) - eqiOf(b);
    }
  };
  const out = [...runs].sort(cmp);
  return desc ? out.reverse() : out;
}

export function filterRuns(runs: RunInfo[], q: string): RunInfo[] {
  const needle = q.trim().toLowerCase();
  if (!needle) return runs;
  return runs.filter((r) =>
    [r.slug, r.client ?? '', r.tier ?? '', r.as_of ?? '', r.verification?.overall_confidence ?? '']
      .join(' ')
      .toLowerCase()
      .includes(needle),
  );
}

export const RunsTable: React.FC<{ runs: RunInfo[]; cursor: number; width: number; height: number }> = ({
  runs,
  cursor,
  width,
  height,
}) => {
  const ic = useIcon();
  // Column sets by width: narrow < 100 <= medium < 130 <= wide.
  const wide = width >= 130;
  const medium = width >= 100;
  const fixed = 2 + 13 + 11 + (medium ? 21 + 11 + 5 + 10 : 0) + (wide ? 11 + 4 : 0);
  const slugW = Math.max(12, Math.min(40, width - 8 - fixed));
  const start = Math.max(0, Math.min(cursor - Math.floor(height / 2), runs.length - height));
  const shown = runs.slice(start, start + height);
  return (
    <Box flexDirection="column">
      <Line>
        <Txt dim>
          {'  '}
          {pad('slug', slugW)}
          {medium ? ` ${pad('client', 20)}` : ''}
          {wide ? ` ${pad('as of', 10)}` : ''}
          {medium ? ` ${pad('tier', 10)}` : ''}
          {` ${pad('confidence', 12)} ${pad('B/M/m', 10)}`}
          {medium ? ` ${pad('EQI', 4)}` : ''}
          {wide ? ` ${pad('exp', 3)}` : ''}
          {medium ? ' modified' : ''}
        </Txt>
      </Line>
      {shown.map((r, i) => {
        const band = r.verification?.overall_confidence ?? null;
        const sel = start + i === cursor;
        const v = r.verification;
        return (
          <Line key={r.slug} selected={sel}>
            <Txt tone={bandTone(band)}>{ic(r.dossier ? 'done' : 'pending')} </Txt>
            <Txt bold={sel} tone={sel ? 'accent' : undefined}>
              {pad(r.slug, slugW)}
            </Txt>
            {medium ? <Txt> {pad(r.client ?? '-', 20)}</Txt> : null}
            {wide ? <Txt dim> {pad(r.as_of ?? '-', 10)}</Txt> : null}
            {medium ? <Txt> {pad(r.tier ?? '-', 10)}</Txt> : null}
            <Txt tone={bandTone(band)}> {pad(band ?? 'unverified', 12)}</Txt>
            <Txt tone={(v?.blockers ?? 0) > 0 ? 'err' : undefined} dim={!v?.blockers}> {pad(v ? vmm(v) : '-', 10)}</Txt>
            {medium ? <Txt dim> {pad(fmtEqi(v?.eqi), 4)}</Txt> : null}
            {wide ? <Txt dim> {pad(String(r.exports?.length ?? 0), 3)}</Txt> : null}
            {medium ? <Txt dim> {ago(r.mtime)}</Txt> : null}
          </Line>
        );
      })}
      {runs.length > height ? (
        <Txt dim>
          {'  '}
          {start + 1}-{Math.min(runs.length, start + height)} of {runs.length}
        </Txt>
      ) : null}
    </Box>
  );
};

// The browser keeps its sort, filter and cursor across a detail view and back.
const view = { cursor: 0, sort: 'modified' as SortKey, desc: true, filter: '' };

export const Runs: React.FC = () => {
  const ctx = useAppCtx();
  const ui = useUi();
  const runs = useEngine(() => ctx.bridge.runsList());
  const [cursor, setCursor] = useState(view.cursor);
  const [sort, setSort] = useState<SortKey>(view.sort);
  const [desc, setDesc] = useState(view.desc);
  const [filter, setFilter] = useState(view.filter);
  const [filtering, setFiltering] = useState(false);
  Object.assign(view, { cursor, sort, desc, filter });

  const list = sortRuns(filterRuns(runs.data ?? [], filter), sort, desc);
  const cur = Math.min(cursor, Math.max(0, list.length - 1));

  useKeys((input, key) => {
    if (filtering) {
      if (key.escape) {
        setFilter('');
        setFiltering(false);
      } else if (key.upArrow || key.downArrow) {
        setFiltering(false);
        return false;
      }
      return true;
    }
    if (key.upArrow || input === 'k') {
      setCursor(Math.max(0, cur - 1));
      return true;
    }
    if (key.downArrow || input === 'j') {
      setCursor(Math.min(list.length - 1, cur + 1));
      return true;
    }
    if (key.pageUp) {
      setCursor(Math.max(0, cur - 10));
      return true;
    }
    if (key.pageDown) {
      setCursor(Math.min(list.length - 1, cur + 10));
      return true;
    }
    if (input === 's') {
      setSort(SORTS[(SORTS.indexOf(sort) + 1) % SORTS.length]);
      return true;
    }
    if (input === 'S' || input === 'R') {
      setDesc((d) => !d);
      return true;
    }
    if (input === '/') {
      setFiltering(true);
      return true;
    }
    if (input === 'r' || input === 'g') {
      runs.reload();
      return true;
    }
    const r = list[cur];
    if (!r) return false;
    if (key.return) {
      ctx.go('runDetail', { slug: r.slug });
      return true;
    }
    if (input === 'e') {
      ctx.go('export', { dossier: r.run_dir, slug: r.slug });
      return true;
    }
    if (input === 'o') {
      void openPath(r.run_dir).then((ok) => ctx.toast(ok ? `opened ${shortPath(r.run_dir)}` : 'could not open a file manager', ok ? 'ok' : 'warn'));
      return true;
    }
    if (input === 'c') {
      const p = r.dossier ?? r.run_dir;
      void copyText(p).then((ok) => ctx.toast(ok ? `copied ${shortPath(p)}` : `no clipboard tool - path: ${p}`, ok ? 'ok' : 'warn'));
      return true;
    }
    return false;
  });

  return (
    <Panel
      title={`Runs${runs.data ? ` (${list.length}${filter ? ` of ${runs.data.length}` : ''})` : ''}`}
      icon="runs"
      focused
      right={
        <Txt dim>
          sort {sort} {desc ? 'desc' : 'asc'}
        </Txt>
      }
    >
      {filtering || filter ? (
        <Box>
          <Icon name="filter" tone="accent" />
          {filtering ? (
            <TextInput value={filter} onChange={(v) => { setFilter(v); setCursor(0); }} onSubmit={() => setFiltering(false)} focus />
          ) : (
            <Txt>{filter}</Txt>
          )}
        </Box>
      ) : null}
      {runs.loading ? (
        <Loading label="listing runs" />
      ) : runs.error ? (
        <ErrorPanel message={runs.error} />
      ) : list.length ? (
        <RunsTable runs={list} cursor={cur} width={ui.width} height={Math.max(5, ui.height - 14)} />
      ) : (
        <Txt dim>{filter ? 'no runs match the filter' : 'no runs found'}</Txt>
      )}
    </Panel>
  );
};

export const RUNS_KEYS: [string, string][] = [
  ['up/down', 'move'],
  ['enter', 'open run detail'],
  ['s / S', 'cycle sort key / reverse order'],
  ['/', 'filter'],
  ['e', 'export the selected dossier'],
  ['o', 'open the run folder'],
  ['c', 'copy the dossier path'],
  ['r', 'reload'],
];

export const RunDetail: React.FC<{ slug: string }> = ({ slug }) => {
  const ctx = useAppCtx();
  const ui = useUi();
  const ic = useIcon();
  const run = useEngine(() => ctx.bridge.runsShow(slug), [slug]);
  const [scroll, setScroll] = useState(0);

  const r = run.data;
  const sections = r?.sections ?? [];
  const secH = Math.max(4, ui.height - 22);

  useKeys((input, key) => {
    if (input === 'r') {
      run.reload();
      return true;
    }
    if (!r) return false;
    if (key.downArrow || input === 'j') {
      setScroll((s) => Math.min(Math.max(0, sections.length - secH), s + 1));
      return true;
    }
    if (key.upArrow || input === 'k') {
      setScroll((s) => Math.max(0, s - 1));
      return true;
    }
    if (input === 'e') {
      ctx.go('export', { dossier: r.run_dir, slug: r.slug });
      return true;
    }
    if (input === 'o') {
      void openPath(r.run_dir).then((ok) => ctx.toast(ok ? `opened ${shortPath(r.run_dir)}` : 'could not open a file manager', ok ? 'ok' : 'warn'));
      return true;
    }
    if (input === 'c') {
      const p = r.dossier ?? r.run_dir;
      void copyText(p).then((ok) => ctx.toast(ok ? `copied ${shortPath(p)}` : `no clipboard tool - path: ${p}`, ok ? 'ok' : 'warn'));
      return true;
    }
    return false;
  });

  if (run.loading) return <Loading label={`loading ${slug}`} />;
  if (run.error || !r) return <ErrorPanel message={run.error ?? 'run not found'} />;

  const v = r.verification;
  const band = v?.overall_confidence ?? null;
  const topics = v?.budget_limited_topics ?? [];
  const valueW = Math.max(20, ui.width - 20);

  return (
    <Box flexDirection="column">
      <Panel title={r.slug} icon="runs" focused right={<Txt dim>{ago(r.mtime)}</Txt>}>
        <Field label="client">
          <Txt bold>{r.client ?? '-'}</Txt>
        </Field>
        <Field label="as of">
          <Txt>{r.as_of ?? '-'}</Txt>
        </Field>
        <Field label="tier">
          <Txt>{r.tier ?? '-'}</Txt>
        </Field>
        <Field label="run dir">
          <Txt wrap="truncate-middle">{truncate(shortPath(r.run_dir), valueW)}</Txt>
        </Field>
        <Field label="dossier">
          <Txt bold wrap="truncate-middle">{r.dossier ? truncate(shortPath(r.dossier), valueW) : '(none)'}</Txt>
        </Field>
      </Panel>
      <Box flexDirection={ui.narrow ? 'column' : 'row'}>
        <Panel title="Verification" icon="shield" tone={bandTone(band)} flexGrow={1} flexShrink={0} minWidth={46}>
          {v ? (
            <>
              <Field label="result" width={16}>
                <Txt bold>{String(v.result ?? '-')}</Txt>
              </Field>
              <Field label="confidence" width={16}>
                <Txt tone={bandTone(band)} bold>
                  {band ?? '-'}
                </Txt>
              </Field>
              <Field label="EQI" width={16}>
                <Txt>{fmtEqi(v.eqi)}</Txt>
              </Field>
              <Field label="findings" width={16}>
                <Txt>
                  <Txt tone={(v.blockers ?? 0) > 0 ? 'err' : 'ok'}>{v.blockers ?? 0} BLOCKER</Txt>
                  <Txt dim>  </Txt>
                  <Txt tone={(v.majors ?? 0) > 0 ? 'warn' : 'ok'}>{v.majors ?? 0} MAJOR</Txt>
                  <Txt dim>  </Txt>
                  <Txt>{v.minors ?? 0} minor</Txt>
                </Txt>
              </Field>
              {band === 'Insufficient' ? <Txt tone="err">do not present - re-run with better sources or reduce scope</Txt> : null}
              <Field label="budget-limited" width={16}>
                {topics && topics.length ? (
                  <Txt tone="warn" wrap="wrap">
                    {topics.join(', ')}
                  </Txt>
                ) : (
                  <Txt dim>none</Txt>
                )}
              </Field>
            </>
          ) : (
            <Txt dim>no verification report</Txt>
          )}
        </Panel>
        <Panel title={`Exports (${r.exports?.length ?? 0})`} icon="export" flexGrow={1}>
          {r.exports?.length ? (
            r.exports.slice(0, 8).map((e) => (
              <Txt key={e} wrap="truncate-middle">
                {ic('file')} {shortPath(e)}
              </Txt>
            ))
          ) : (
            <Txt dim>none yet - press e to export</Txt>
          )}
        </Panel>
      </Box>
      <Panel title={`Sections (${sections.length})`} icon="file">
        {sections.length ? (
          sections.slice(scroll, scroll + secH).map((s) => (
            <Txt key={s} wrap="truncate">
              {ic('file')} {s}
            </Txt>
          ))
        ) : (
          <Txt dim>no section files listed</Txt>
        )}
        {sections.length > secH ? (
          <Txt dim>
            {scroll + 1}-{Math.min(sections.length, scroll + secH)} of {sections.length}
          </Txt>
        ) : null}
      </Panel>
    </Box>
  );
};

export const DETAIL_KEYS: [string, string][] = [
  ['up/down', 'scroll sections'],
  ['e', 'export this dossier'],
  ['o', 'open the run folder'],
  ['c', 'copy the dossier path'],
  ['r', 'reload'],
  ['esc', 'back to the list'],
];
