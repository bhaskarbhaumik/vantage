// Home dashboard: version, auth mode, defaults, recent runs and quick actions.
import React, { useEffect, useRef } from 'react';
import { Box } from 'ink';
import SelectInput from 'ink-select-input';
import { useAppCtx, useEngine, type ScreenId } from '../components/context.js';
import { AuthBadge, ErrorPanel, Field, Icon, Line, Loading, Panel, Txt, useIcon, useUi } from '../components/ui.js';
import { getPath } from '../lib/config.js';
import { ago, pad, truncate, vmm } from '../lib/format.js';
import { bandTone } from '../lib/theme.js';
import type { RunInfo } from '../lib/engine.js';

export const RecentRuns: React.FC<{ runs: RunInfo[]; limit?: number; width: number }> = ({ runs, limit = 6, width }) => {
  const ic = useIcon();
  const slugW = Math.max(14, Math.min(34, width - 50));
  const sorted = [...runs].sort((a, b) => (b.mtime ?? 0) - (a.mtime ?? 0)).slice(0, limit);
  if (!sorted.length) return <Txt dim>No runs yet. Press 2 to start a dossier.</Txt>;
  return (
    <Box flexDirection="column">
      {sorted.map((r) => {
        const band = r.verification?.overall_confidence ?? null;
        return (
          <Line key={r.slug} pointer={false}>
            <Txt tone={bandTone(band)}>{ic(r.dossier ? 'done' : 'pending')} </Txt>
            <Txt bold>{pad(r.slug, slugW)}</Txt>
            <Txt tone={bandTone(band)}> {pad(band ?? 'unverified', 13)}</Txt>
            <Txt dim> {pad(vmm(r.verification), 10)}</Txt>
            <Txt dim> {ago(r.mtime)}</Txt>
          </Line>
        );
      })}
    </Box>
  );
};

interface Item {
  label: string;
  value: ScreenId;
}

export const Home: React.FC = () => {
  const ctx = useAppCtx();
  const ui = useUi();
  const ic = useIcon();
  const version = useEngine(() => ctx.bridge.version());
  const runs = useEngine(() => ctx.bridge.runsList());
  const auth = String(getPath(ctx.localConfig, 'auth.mode') ?? ctx.defaults.authMode);
  // ink-select-input also selects on digit keys, which are global screen shortcuts here. Defer the
  // navigation one tick: when a digit already switched screens this component is gone by then.
  const mounted = useRef(true);
  useEffect(
    () => () => {
      mounted.current = false;
    },
    [],
  );

  const items: Item[] = [
    { label: `${ic('newRun')} New dossier`, value: 'run' },
    { label: `${ic('runs')} Browse runs`, value: 'runs' },
    { label: `${ic('export')} Export a dossier`, value: 'export' },
    { label: `${ic('doctor')} Doctor`, value: 'doctor' },
    { label: `${ic('backends')} Backends`, value: 'backends' },
    { label: `${ic('config')} Configuration`, value: 'config' },
  ];
  if (ctx.run.active || ctx.run.state.status !== 'idle') {
    items.unshift({ label: `${ic('live')} Live run (${ctx.run.state.status})`, value: 'live' });
  }

  const status = (
    <Panel title="Engine" icon="plug" flexGrow={1}>
      <Field label="version">
        {version.loading ? (
          <Loading label="asking the engine" />
        ) : version.data ? (
          <Txt>
            {version.data.version}
            {version.data.harness ? <Txt dim>  harness {version.data.harness}</Txt> : null}
            {version.data.config ? <Txt dim>  config {version.data.config}</Txt> : null}
          </Txt>
        ) : (
          <Txt tone="warn">unavailable</Txt>
        )}
      </Field>
      <Field label="tui">
        <Txt>{ctx.tuiVersion}</Txt>
      </Field>
      <Field label="auth">
        <AuthBadge mode={auth} />
      </Field>
      <Field label="backend">
        <Txt bold>{ctx.defaults.backend}</Txt>
      </Field>
      <Field label="tier">
        <Txt bold>{ctx.defaults.tier}</Txt>
      </Field>
      <Field label="engine cmd">
        <Txt dim wrap="truncate">{truncate(ctx.bridge.describe(), Math.max(20, ui.width - 30))}</Txt>
      </Field>
    </Panel>
  );

  const actions = (
    <Panel title="Quick actions" icon="rocket" minWidth={30}>
      <SelectInput<ScreenId>
        items={items}
        indicatorComponent={({ isSelected }) => (
          <Txt tone="accent" bold>
            {isSelected ? `${ic('pointer')} ` : '  '}
          </Txt>
        )}
        itemComponent={({ isSelected, label }) => (
          <Txt tone={isSelected ? 'accent' : undefined} bold={isSelected}>
            {label}
          </Txt>
        )}
        isFocused={!ctx.modal}
        onSelect={(it) => {
          setTimeout(() => {
            if (mounted.current) ctx.go(it.value);
          }, 0);
        }}
      />
    </Panel>
  );

  return (
    <Box flexDirection="column">
      <Box flexDirection={ui.narrow ? 'column' : 'row'}>
        {status}
        {actions}
      </Box>
      {version.error ? <ErrorPanel title="Engine unavailable" message={version.error} hint="" /> : null}
      <Panel title="Recent runs" icon="runs" right={<Txt dim>4 browse all</Txt>}>
        {runs.loading ? (
          <Loading label="listing runs" />
        ) : runs.error ? (
          <Box>
            <Icon name="warn" tone="warn" />
            <Txt tone="warn" wrap="truncate">
              {runs.error.split('\n')[0]}
            </Txt>
          </Box>
        ) : (
          <RecentRuns runs={runs.data ?? []} width={ui.width} />
        )}
      </Panel>
    </Box>
  );
};
