// Doctor and Backends views: environment checks and backend readiness.
import React, { useState } from 'react';
import { Box } from 'ink';
import { useAppCtx, useEngine, useKeys } from '../components/context.js';
import { Badge, ErrorPanel, Line, Loading, Panel, Txt, useIcon, useUi } from '../components/ui.js';
import type { Check } from '../lib/engine.js';
import { pad } from '../lib/format.js';
import type { Tone } from '../lib/theme.js';

function checkTone(status: string): Tone {
  return status === 'ok' ? 'ok' : status === 'warn' ? 'warn' : 'err';
}

export function groupChecks(checks: Check[]): [string, Check[]][] {
  const groups = new Map<string, Check[]>();
  for (const c of checks) {
    const g = c.group || 'general';
    groups.set(g, [...(groups.get(g) ?? []), c]);
  }
  return [...groups.entries()];
}

export const Doctor: React.FC = () => {
  const ctx = useAppCtx();
  const ui = useUi();
  const ic = useIcon();
  const doc = useEngine(() => ctx.bridge.doctor());
  const [onlyProblems, setOnlyProblems] = useState(false);

  useKeys((input) => {
    if (input === 'r') {
      doc.reload();
      return true;
    }
    if (input === 'f') {
      setOnlyProblems((x) => !x);
      return true;
    }
    return false;
  });

  if (doc.loading) return <Loading label="running checks (this can take a few seconds)" />;
  if (doc.error || !doc.data) return <ErrorPanel title="Doctor unavailable" message={doc.error ?? 'no data'} />;

  const checks = onlyProblems ? doc.data.checks.filter((c) => c.status !== 'ok') : doc.data.checks;
  const counts = { ok: 0, warn: 0, fail: 0 };
  for (const c of doc.data.checks) {
    if (c.status === 'ok') counts.ok++;
    else if (c.status === 'warn') counts.warn++;
    else counts.fail++;
  }
  const nameW = ui.narrow ? 20 : 28;

  return (
    <Panel
      title={`Doctor${doc.data.version ? ` - engine ${doc.data.version}` : ''}`}
      icon="doctor"
      focused
      right={
        <Box>
          <Badge tone="ok" icon="ok">{counts.ok}</Badge>
          <Txt> </Txt>
          <Badge tone="warn" icon="warn">{counts.warn}</Badge>
          <Txt> </Txt>
          <Badge tone="err" icon="fail">{counts.fail}</Badge>
        </Box>
      }
    >
      {groupChecks(checks).map(([group, list]) => (
        <Box key={group} flexDirection="column" marginTop={1}>
          <Txt tone="accent2" bold>
            {group}
          </Txt>
          {list.map((c, i) => (
            <Line key={`${c.name}-${i}`} pointer={false}>
              <Txt tone={checkTone(c.status)}>{ic(c.status === 'ok' ? 'ok' : c.status === 'warn' ? 'warn' : 'fail')} </Txt>
              <Txt bold={c.status !== 'ok'}>{pad(c.name, nameW)}</Txt>
              <Txt dim={c.status === 'ok'} tone={c.status === 'ok' ? undefined : checkTone(c.status)}>
                {' '}
                {c.detail}
              </Txt>
            </Line>
          ))}
        </Box>
      ))}
      {!checks.length ? <Txt tone="ok">no problems found</Txt> : null}
    </Panel>
  );
};

export const DOCTOR_KEYS: [string, string][] = [
  ['r', 're-run the checks'],
  ['f', 'show only warnings and failures'],
];

export const Backends: React.FC = () => {
  const ctx = useAppCtx();
  const ic = useIcon();
  const be = useEngine(() => ctx.bridge.backends());
  const [cursor, setCursor] = useState(0);

  const list = be.data?.backends ?? [];
  useKeys((input, key) => {
    if (input === 'r') {
      be.reload();
      return true;
    }
    if (key.upArrow || input === 'k') {
      setCursor((c) => Math.max(0, c - 1));
      return true;
    }
    if (key.downArrow || input === 'j') {
      setCursor((c) => Math.min(list.length - 1, c + 1));
      return true;
    }
    if (key.return && list[cursor]) {
      ctx.go('run', { backend: list[cursor].name });
      return true;
    }
    return false;
  });

  if (be.loading) return <Loading label="probing backends" />;
  if (be.error || !be.data) return <ErrorPanel title="Backends unavailable" message={be.error ?? 'no data'} />;

  return (
    <Panel title="Backends" icon="backends" focused right={<Txt dim>default {be.data.default}</Txt>}>
      {list.map((b, i) => (
        <Box key={b.name} flexDirection="column">
          <Line selected={i === cursor}>
            <Txt tone={b.ready ? 'ok' : 'err'}>{ic(b.ready ? 'ok' : 'fail')} </Txt>
            <Txt bold>{pad(b.name, 12)}</Txt>
            <Txt tone={b.ready ? 'ok' : 'err'}>{b.ready ? 'ready' : 'not ready'}</Txt>
            {b.name === be.data!.default ? <Txt tone="accent"> (default)</Txt> : null}
          </Line>
          {(b.issues ?? []).map((iss, j) => (
            <Box key={j} marginLeft={6}>
              <Txt tone="warn" wrap="truncate">
                {ic('warn')} {iss}
              </Txt>
            </Box>
          ))}
        </Box>
      ))}
      <Box marginTop={1}>
        <Txt dim>enter start a dossier on the selected backend</Txt>
      </Box>
    </Panel>
  );
};

export const BACKENDS_KEYS: [string, string][] = [
  ['up/down', 'move'],
  ['enter', 'new dossier on this backend'],
  ['r', 'reload'],
];
