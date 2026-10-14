// Live run dashboard: phase timeline, agent grid, log and warnings panes, totals and clock.
import React, { useEffect, useState } from 'react';
import { Box } from 'ink';
import TextInput from 'ink-text-input';
import { useAppCtx, useKeys } from '../components/context.js';
import { AuthBadge, Bar, Icon, Panel, Spin, Txt, useIcon, useUi } from '../components/ui.js';
import { elapsed, fmtEqi, pad, padStart, shortPath, tokens, truncate, vmm } from '../lib/format.js';
import type { IconName } from '../lib/icons.js';
import { type AgentState, type LogLine, type PhaseState, progress, type RunState } from '../lib/runState.js';
import { bandTone, type Tone } from '../lib/theme.js';

const PHASE_TONE: Record<PhaseState['status'], Tone> = {
  pending: 'muted',
  running: 'info',
  done: 'ok',
  error: 'err',
  skipped: 'muted',
};

const PHASE_ICON: Record<PhaseState['status'], IconName> = {
  pending: 'pending',
  running: 'running',
  done: 'ok',
  error: 'fail',
  skipped: 'skipped',
};

const LOG_TONE: Record<LogLine['level'], Tone | undefined> = {
  info: undefined,
  stage: 'accent',
  tool: 'muted',
  ok: 'ok',
  warn: 'warn',
  error: 'err',
};

function useClock(active: boolean): number {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!active) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [active]);
  return now;
}

export const Timeline: React.FC<{ phases: PhaseState[] }> = ({ phases }) => {
  const ic = useIcon();
  return (
    <Box flexWrap="wrap">
      {phases.map((p, i) => (
        <Box key={p.key} marginRight={1}>
          {p.status === 'running' ? <Spin /> : <Txt tone={PHASE_TONE[p.status]}>{ic(PHASE_ICON[p.status])}</Txt>}
          <Txt tone={PHASE_TONE[p.status]} bold={p.status === 'running'} dim={p.status === 'skipped'}>
            {' '}
            {p.key}
          </Txt>
          {i < phases.length - 1 ? <Txt dim> {ic('link')}</Txt> : null}
        </Box>
      ))}
    </Box>
  );
};

export const AgentGrid: React.FC<{ agents: AgentState[]; width: number; now: number; maxRows: number }> = ({
  agents,
  width,
  now,
  maxRows,
}) => {
  const ic = useIcon();
  const cols = width >= 150 ? 3 : width >= 96 ? 2 : 1;
  const cellW = Math.max(30, Math.floor((width - 2) / cols) - 1);
  const labelW = Math.max(10, cellW - 22);
  // Running agents first, then errors, then the most recent finishers.
  const ordered = [...agents].sort((a, b) => {
    const rank = (x: AgentState) => (x.status === 'running' ? 0 : x.status === 'error' ? 1 : 2);
    return rank(a) - rank(b) || (b.endedAt ?? b.startedAt) - (a.endedAt ?? a.startedAt);
  });
  const capacity = cols * maxRows;
  const shown = ordered.slice(0, capacity);
  const rows: AgentState[][] = [];
  for (let r = 0; r < Math.ceil(shown.length / cols); r++) rows.push(shown.slice(r * cols, r * cols + cols));
  if (!agents.length) return <Txt dim>waiting for the first agent...</Txt>;
  return (
    <Box flexDirection="column">
      {rows.map((row, ri) => (
        <Box key={ri}>
          {row.map((a) => (
            <Box key={a.label} width={cellW} marginRight={1}>
              <Txt wrap="truncate">
                {a.status === 'running' ? (
                  <Spin />
                ) : (
                  <Txt tone={a.status === 'done' ? 'ok' : 'err'}>{ic(a.status === 'done' ? 'ok' : 'fail')}</Txt>
                )}
                <Txt bold={a.status === 'running'}> {pad(a.label, labelW)}</Txt>
                <Txt dim>{padStart(elapsed((a.endedAt ?? now) - a.startedAt), 7)}</Txt>
                <Txt tone="accent2">{padStart(tokens(a.outputTokens), 7)}</Txt>
              </Txt>
            </Box>
          ))}
        </Box>
      ))}
      {ordered.length > capacity ? <Txt dim>+{ordered.length - capacity} more finished agents</Txt> : null}
    </Box>
  );
};

export const ResultSummary: React.FC<{ state: RunState }> = ({ state }) => {
  const r = state.result;
  const v = r?.verification ?? null;
  const band = v?.overall_confidence ?? null;
  const topics = v?.budget_limited_topics ?? [];
  const ok = state.status === 'done' && Boolean(r?.dossier);
  return (
    <Panel
      title={ok ? 'Dossier ready' : state.status === 'cancelled' ? 'Run cancelled' : 'Run did not produce a dossier'}
      icon={ok ? 'done' : 'error'}
      tone={ok ? 'ok' : 'err'}
    >
      <Box>
        <Box width={12}><Txt dim>agents</Txt></Box>
        <Txt>{r?.agentsOk ?? state.totals.agentsOk}/{r?.agentsTotal ?? state.totals.agentsTotal} ok</Txt>
      </Box>
      {v ? (
        <Box>
          <Box width={12}><Txt dim>verify</Txt></Box>
          <Txt>{String(v.result ?? '-')} </Txt>
          <Txt tone={bandTone(band)} bold>{band ?? '-'}</Txt>
          <Txt> EQI {fmtEqi(v.eqi)}  {vmm(v)}</Txt>
        </Box>
      ) : null}
      {band === 'Insufficient' ? <Txt tone="err">do not present - re-run with better sources or reduce scope</Txt> : null}
      {topics && topics.length ? (
        <Txt tone="warn" wrap="wrap">stopped on budget (not diminishing returns): {topics.join(', ')}</Txt>
      ) : null}
      {r?.entityAmbiguity ? <Txt tone="warn">entity ambiguity: {r.entityAmbiguity}</Txt> : null}
      <Box>
        <Box width={12}><Txt dim>tokens</Txt></Box>
        <Txt>{tokens(state.totals.inputTokens)} in / {tokens(state.totals.outputTokens)} out</Txt>
      </Box>
      <Box>
        <Box width={12}><Txt dim>dossier</Txt></Box>
        <Txt bold wrap="truncate-middle">{r?.dossier ? shortPath(r.dossier) : '(none)'}</Txt>
      </Box>
    </Panel>
  );
};

export const Live: React.FC = () => {
  const ctx = useAppCtx();
  const ui = useUi();
  const ic = useIcon();
  const { state, params } = ctx.run;
  const running = state.status === 'running';
  const now = useClock(running);
  const [follow, setFollow] = useState(true);
  const [showLog, setShowLog] = useState(true);
  const [offset, setOffset] = useState(0);
  const [filter, setFilter] = useState('');
  const [filtering, setFiltering] = useState(false);

  const logH = ui.narrow ? 6 : 8;
  const lines = filter
    ? state.logs.filter((l) => `${l.source} ${l.text}`.toLowerCase().includes(filter.toLowerCase()))
    : state.logs;
  const maxOffset = Math.max(0, lines.length - logH);
  const off = follow ? 0 : Math.min(offset, maxOffset);
  const visible = lines.slice(Math.max(0, lines.length - logH - off), lines.length - off);

  const quit = () =>
    ctx.confirm(
      running ? 'A run is in progress. Quit the TUI and stop the engine?' : 'Quit Vantage?',
      () => ctx.quit(),
      'Quit',
    );

  useKeys((input, key) => {
    if (filtering) {
      if (key.escape) {
        setFilter('');
        setFiltering(false);
      }
      return true;
    }
    if (input === 'q') {
      quit();
      return true;
    }
    if (input === 'p') {
      setFollow((f) => !f);
      setOffset(0);
      return true;
    }
    if (input === 'l') {
      setShowLog((s) => !s);
      return true;
    }
    if (input === '/') {
      setFiltering(true);
      return true;
    }
    if (key.upArrow || key.pageUp || input === 'k') {
      setFollow(false);
      setOffset((o) => Math.min(maxOffset, o + (key.pageUp ? logH : 1)));
      return true;
    }
    if (key.downArrow || key.pageDown || input === 'j') {
      setOffset((o) => Math.max(0, o - (key.pageDown ? logH : 1)));
      return true;
    }
    if (input === 'c' && running) {
      ctx.confirm('Cancel this run? The engine process is stopped; partial output stays on disk.', () => ctx.run.cancel(), 'Cancel run');
      return true;
    }
    if (input === 'e' && state.result?.dossier) {
      ctx.go('export', { dossier: state.result.runDir ?? state.result.dossier });
      return true;
    }
    if (input === 'r' && !running && state.result?.slug) {
      ctx.go('runDetail', { slug: state.result.slug });
      return true;
    }
    return false;
  });

  if (state.status === 'idle') {
    return (
      <Panel title="Live run" icon="live">
        <Txt dim>No run in progress. Press 2 to start a new dossier.</Txt>
      </Panel>
    );
  }

  const start = state.startedAt ?? now;
  const clock = elapsed((state.endedAt ?? now) - start);
  const frac = progress(state);
  const cur = state.phases.find((p) => p.key === state.currentPhase);
  const barW = Math.max(10, Math.min(40, ui.width - 60));
  const agentRows = ui.narrow ? 8 : 10;

  const warnings = (
    <Panel title={`Warnings (${state.warnings.length + state.errors.length})`} icon="warn" tone={state.errors.length ? 'err' : 'warn'} width={ui.narrow ? undefined : Math.max(34, Math.floor(ui.width * 0.32))}>
      {state.errors.length + state.warnings.length === 0 ? <Txt dim>none</Txt> : null}
      {state.errors.slice(-4).map((e, i) => (
        <Txt key={`e${i}`} tone="err" wrap="truncate">
          {ic('error')} {e}
        </Txt>
      ))}
      {state.warnings.slice(-6).map((w, i) => (
        <Txt key={`w${i}`} tone="warn" wrap="truncate">
          {ic('warn')} {w}
        </Txt>
      ))}
    </Panel>
  );

  return (
    <Box flexDirection="column">
      <Panel
        title={`${state.client ?? params?.client ?? 'run'}${params?.slug ? `  ${ic('dot')} ${params.slug}` : ''}`}
        icon="live"
        focused={running}
        right={
          <Box>
            <Icon name="clock" tone="muted" />
            <Txt bold>{clock}</Txt>
          </Box>
        }
      >
        <Box flexWrap="wrap">
          <Txt dim>backend </Txt>
          <Txt bold>{params?.backend ?? ctx.defaults.backend}</Txt>
          <Txt dim>  tier </Txt>
          <Txt bold>{params?.tier ?? ctx.defaults.tier}</Txt>
          <Txt>  </Txt>
          <AuthBadge mode={params?.authMode ?? 'subscription'} />
          <Txt dim>  status </Txt>
          <Txt bold tone={state.status === 'running' ? 'info' : state.status === 'done' ? 'ok' : 'err'}>
            {state.status}
          </Txt>
        </Box>
        <Box marginTop={1}>
          <Timeline phases={state.phases} />
        </Box>
        {!state.sawStages ? (
          <Txt dim>
            {state.inferred ? 'phases inferred from the engine log' : 'this backend streams text only; phases appear as the log names them'}
          </Txt>
        ) : null}
        <Box>
          <Bar fraction={frac} width={barW} tone={state.status === 'failed' ? 'err' : 'accent'} />
          <Txt> {Math.round(frac * 100)}%  </Txt>
          {cur ? (
            <Txt tone="info">
              {cur.key} {cur.title}
              {cur.steps.length ? <Txt dim> ({truncate(cur.steps[cur.steps.length - 1], 30)})</Txt> : null}
            </Txt>
          ) : null}
        </Box>
        <Box>
          <Icon name="agent" tone="accent" />
          <Txt>
            {state.totals.agentsOk}/{state.totals.agentsTotal} agents ok
          </Txt>
          {state.totals.agentsError ? <Txt tone="err">  {state.totals.agentsError} failed</Txt> : null}
          <Txt>  </Txt>
          <Icon name="tokens" tone="accent2" />
          <Txt>
            {tokens(state.totals.inputTokens)} in / {tokens(state.totals.outputTokens)} out
          </Txt>
        </Box>
      </Panel>

      <Box flexDirection={ui.narrow ? 'column' : 'row'}>
        <Panel title={`Agents (${state.agents.length})`} icon="agent" flexGrow={1}>
          <AgentGrid agents={state.agents} width={ui.narrow ? ui.width - 4 : Math.floor(ui.width * 0.66)} now={now} maxRows={agentRows} />
        </Panel>
        {warnings}
      </Box>

      {state.status !== 'running' ? <ResultSummary state={state} /> : null}

      {showLog ? (
        <Panel
          title={`Log${filter ? ` (filter: ${filter})` : ''}`}
          icon="log"
          right={
            <Box>
              {follow ? <Txt dim>follow</Txt> : <Txt tone="warn">{ic('paused')} paused +{off}</Txt>}
            </Box>
          }
        >
          {filtering ? (
            <Box>
              <Icon name="filter" tone="accent" />
              <TextInput value={filter} onChange={setFilter} onSubmit={() => setFiltering(false)} focus />
            </Box>
          ) : null}
          {visible.length ? (
            visible.map((l, i) => (
              <Txt key={`${l.ts}-${i}`} wrap="truncate">
                <Txt dim>{pad(l.source, ui.narrow ? 12 : 18)} </Txt>
                <Txt tone={LOG_TONE[l.level]}>{l.text}</Txt>
              </Txt>
            ))
          ) : (
            <Txt dim>{filter ? 'no matching lines' : 'no log lines yet'}</Txt>
          )}
        </Panel>
      ) : null}
    </Box>
  );
};

export const LIVE_KEYS: [string, string][] = [
  ['p', 'pause/resume log autoscroll'],
  ['l', 'show/hide the log'],
  ['/', 'filter the log'],
  ['up/down pgup/pgdn', 'scroll the log'],
  ['c', 'cancel the run'],
  ['e', 'export the finished dossier'],
  ['r', 'open the finished run'],
  ['q', 'quit (asks first)'],
];
