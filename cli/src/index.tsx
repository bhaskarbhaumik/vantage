#!/usr/bin/env node
import React, { useEffect, useState } from 'react';
import { Box, render, Text, useApp, useInput } from 'ink';
import SelectInput from 'ink-select-input';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import { parseArgs, PASSTHROUGH } from './lib/args.js';
import { loadDefaults } from './lib/config.js';
import { passthrough, runEngine, type RunEvent, type RunParams } from './lib/engine.js';

const BRAND = '#4E84C4'; // Accent blue

type Phase = 'client' | 'slug' | 'backend' | 'tier' | 'running' | 'done';

const TIERS = [
  { value: 'FULL_ANNEX', hint: '— all 22 sections + full appendices (default)' },
  { value: 'STANDARD', hint: '— §0-§20, condensed appendices' },
  { value: 'EXECUTIVE', hint: '— §0-§2 + synthesis only, single research wave' },
];
type AgentStatus = 'run' | 'done' | 'error';
interface AgentRow { label: string; status: AgentStatus; note?: string }

function slugify(name: string): string {
  const base = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 32);
  const d = new Date();
  return `${base || 'client'}-${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

interface AppProps { initial: Partial<RunParams> }

const Header: React.FC<{ sub?: string }> = ({ sub }) => (
  <Box flexDirection="column" marginBottom={1}>
    <Text color={BRAND} bold>Vantage · Verified Account Navigator: Targeting, Analysis & GTM Engine</Text>
    {sub ? <Text dimColor>{sub}</Text> : null}
  </Box>
);

const App: React.FC<AppProps> = ({ initial }) => {
  const { exit } = useApp();
  const defaults = loadDefaults();
  const startPhase: Phase = initial.client && initial.slug ? 'backend' : 'client';

  const [phase, setPhase] = useState<Phase>(startPhase);
  const [client, setClient] = useState(initial.client ?? '');
  const [slug, setSlug] = useState(initial.slug ?? '');
  const [backend, setBackend] = useState(initial.backend ?? defaults.backend);
  const [tier, setTier] = useState(initial.tier ?? defaults.tier);

  const [stage, setStage] = useState('starting…');
  const [agents, setAgents] = useState<AgentRow[]>([]);
  const [outTokens, setOutTokens] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [issues, setIssues] = useState<string[]>([]);

  useInput((input) => {
    if (phase === 'done' && (input === 'q' || input === 'Q')) exit();
  });

  // run
  useEffect(() => {
    if (phase !== 'running') return;
    const params: RunParams = {
      client, slug, backend, tier,
      authMode: initial.authMode, askKey: initial.askKey,
      asOf: initial.asOf, ticker: initial.ticker, vertical: initial.vertical,
      geography: initial.geography, commonName: initial.commonName,
      accountContext: initial.accountContext, relationship: initial.relationship, objectives: initial.objectives,
    };
    const onEvent = (ev: RunEvent) => {
      if (ev.type === 'stage_start') setStage(ev.stage ?? '');
      else if (ev.type === 'agent_start')
        setAgents((a) => (a.find((x) => x.label === ev.agent) ? a : [...a, { label: ev.agent ?? '?', status: 'run' }]));
      else if (ev.type === 'agent_done') {
        setAgents((a) => a.map((x) => (x.label === ev.agent ? { ...x, status: 'done' } : x)));
        const ot = (ev.data?.usage as { output_tokens?: number } | undefined)?.output_tokens ?? 0;
        setOutTokens((t) => t + ot);
      } else if (ev.type === 'agent_error')
        setAgents((a) => a.map((x) => (x.label === ev.agent ? { ...x, status: 'error', note: ev.message ?? '' } : x)));
      else if (ev.type === 'log' && ev.message)
        setLogs((l) => [...l.slice(-6), `${ev.agent ?? ''} ${ev.message}`.trim()]);
      else if ((ev.type === 'run_error' || ev.type === 'run_warning') && ev.message)
        setIssues((s) => [...s, ev.message as string]);
    };
    runEngine(params, onEvent).then((out) => {
      setResult(out.result);
      if (!out.result && out.stderr) setIssues((s) => [...s, out.stderr.split('\n').filter(Boolean).slice(-1)[0] ?? '']);
      setPhase('done');
    });
  }, [phase]); // eslint-disable-line react-hooks/exhaustive-deps

  if (phase === 'client')
    return (
      <Box flexDirection="column"><Header sub="Step 1/4 — client" />
        <Box><Text>Client legal name: </Text>
          <TextInput value={client} onChange={setClient}
            onSubmit={(v) => { if (v.trim()) { setClient(v.trim()); if (!slug) setSlug(slugify(v)); setPhase('slug'); } }} />
        </Box>
      </Box>
    );

  if (phase === 'slug')
    return (
      <Box flexDirection="column"><Header sub="Step 2/4 — run slug" />
        <Box><Text>Run slug: </Text>
          <TextInput value={slug} onChange={setSlug}
            onSubmit={(v) => { setSlug(v.trim() || slugify(client)); setPhase('backend'); }} />
        </Box>
      </Box>
    );

  if (phase === 'backend')
    return (
      <Box flexDirection="column"><Header sub="Step 3/4 — engine backend (default first)" />
        <SelectInput
          items={defaults.backends.map((b) => ({ label: b === defaults.backend ? `${b}  (default)` : b, value: b }))}
          initialIndex={Math.max(0, defaults.backends.indexOf(backend))}
          onSelect={(it) => { setBackend(String(it.value)); setPhase('tier'); }} />
      </Box>
    );

  if (phase === 'tier')
    return (
      <Box flexDirection="column"><Header sub="Step 4/4 — output tier" />
        <SelectInput
          items={TIERS.map((t) => ({ label: `${t.value}  ${t.hint}`, value: t.value }))}
          initialIndex={Math.max(0, TIERS.findIndex((t) => t.value === tier))}
          onSelect={(it) => { setTier(String(it.value)); setPhase('running'); }} />
      </Box>
    );

  if (phase === 'running')
    return (
      <Box flexDirection="column">
        <Header sub={`${client} · ${backend} · ${tier} · ${initial.authMode ?? defaults.authMode}`} />
        <Box><Text color="cyan"><Spinner type="dots" /></Text><Text> {stage}</Text><Text dimColor>   ({outTokens} out tok)</Text></Box>
        <Box flexDirection="column" marginTop={1}>
          {agents.map((a) => (
            <Text key={a.label}>
              {a.status === 'run' ? <Text color="cyan"><Spinner type="dots" /></Text> : a.status === 'done' ? <Text color="green">✓</Text> : <Text color="red">✗</Text>}
              {' '}{a.label}{a.note ? <Text dimColor> — {a.note}</Text> : null}
            </Text>
          ))}
        </Box>
        {logs.length ? <Box flexDirection="column" marginTop={1}>{logs.map((l, i) => <Text key={i} dimColor>{l.slice(0, 100)}</Text>)}</Box> : null}
      </Box>
    );

  // done
  const r = result ?? {};
  const ok = Boolean(r.dossier);
  const ver = (r.verification as Record<string, unknown> | null) ?? null;
  const band = ver ? String(ver.overall_confidence ?? '') : '';
  const budgetTopics = (ver?.budget_limited_topics as string[] | undefined) ?? [];
  return (
    <Box flexDirection="column">
      <Header sub={`${client} · ${backend}`} />
      <Text color={ok ? 'green' : 'red'} bold>{ok ? '● dossier ready' : '● run did not produce a dossier'}</Text>
      <Box flexDirection="column" marginTop={1}>
        <Text>agents    {(r.agents_ok as number) ?? 0}/{(r.agents_total as number) ?? 0} ok</Text>
        {ver ? (
          <Text>
            verify    {String(ver.result)} · <Text color={band === 'Insufficient' ? 'red' : band === 'Thin' ? 'yellow' : 'green'}>{band}</Text>
            {' '}(EQI {String(ver.eqi)}) · {String(ver.blockers ?? 0)}B/{String(ver.majors ?? 0)}M/{String(ver.minors ?? 0)}m
          </Text>
        ) : null}
        {r.entity_ambiguity ? <Text color="yellow">entity    ambiguity: {String(r.entity_ambiguity)}</Text> : null}
        {band === 'Insufficient' ? <Text color="red">          do not present — re-run with better sources or reduce scope</Text> : null}
        {budgetTopics.length ? <Text color="yellow">budget    stopped on budget (not diminishing returns): {budgetTopics.join(', ')}</Text> : null}
        <Text>tokens    {(((r.usage as Record<string, number>) ?? {}).output_tokens) ?? 0} out</Text>
        <Text>dossier   <Text bold>{(r.dossier as string) ?? '(none)'}</Text></Text>
      </Box>
      {issues.length ? <Box flexDirection="column" marginTop={1}>{issues.slice(0, 6).map((e, i) => <Text key={i} color="yellow">! {e}</Text>)}</Box> : null}
      <Box marginTop={1}><Text dimColor>press q to quit</Text></Box>
    </Box>
  );
};

async function main() {
  const argv = process.argv.slice(2);
  const { subcommand, flags } = parseArgs(argv);

  if (subcommand && PASSTHROUGH.has(subcommand)) {
    process.exit(await passthrough(argv));
  }

  const initial: Partial<RunParams> = {
    client: flags.client, slug: flags.slug, backend: flags.backend, tier: flags.tier,
    authMode: flags.auth, askKey: flags['ask-key'] === 'true',
    capabilityPack: flags['capability-pack'], inputSheet: flags['input-sheet'],
    asOf: flags['as-of'], ticker: flags.ticker, vertical: flags.vertical, geography: flags.geography,
    commonName: flags['common-name'], accountContext: flags['account-context'],
    relationship: flags.relationship, objectives: flags.objectives,
  };
  render(<App initial={initial} />);
}

main();
