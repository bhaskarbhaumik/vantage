// New dossier form: every run input, with an explicit cost confirmation for api-key billing.
import React, { useState } from 'react';
import { Box } from 'ink';
import { useAppCtx } from '../components/context.js';
import { Form, type FieldDef, type FieldValue } from '../components/Form.js';
import { AuthBadge, Panel, Txt, useUi } from '../components/ui.js';
import type { RunPrefill } from '../lib/args.js';
import { ATTACH, AUTH_MODES, TIERS } from '../lib/config.js';
import type { RunParams } from '../lib/engine.js';
import { slugify } from '../lib/format.js';

const TIER_LABELS: Record<string, string> = {
  FULL_ANNEX: 'FULL_ANNEX - all sections + full appendices',
  STANDARD: 'STANDARD - condensed appendices',
  EXECUTIVE: 'EXECUTIVE - synthesis only, single wave',
};

export const API_KEY_WARNING =
  'API-key mode bills every input and output token to your provider account at per-token prices. ' +
  'A FULL_ANNEX run fans out to dozens of agents and can consume millions of tokens. ' +
  'Subscription mode runs on your Claude plan and reads no API key.';

export function initialRunValues(prefill: RunPrefill, d: ReturnType<typeof useAppCtx>['defaults']): Record<string, FieldValue> {
  const client = prefill.client ?? '';
  return {
    client,
    slug: prefill.slug ?? (client ? slugify(client) : ''),
    commonName: prefill.commonName ?? '',
    ticker: prefill.ticker ?? '',
    vertical: prefill.vertical ?? '',
    geography: prefill.geography ?? '',
    asOf: prefill.asOf ?? '',
    capabilityPack: prefill.capabilityPack && ATTACH.includes(prefill.capabilityPack) ? prefill.capabilityPack : d.capabilityPack,
    inputSheet: prefill.inputSheet && ATTACH.includes(prefill.inputSheet) ? prefill.inputSheet : d.inputSheet,
    accountContext: prefill.accountContext ?? d.accountContext,
    relationship: prefill.relationship ?? d.relationship,
    objectives: prefill.objectives ?? d.objectives,
    backend: prefill.backend ?? d.backend,
    tier: prefill.tier && TIERS.includes(prefill.tier) ? prefill.tier : d.tier,
    // A deep link never switches billing on silently: api-key still needs the confirmation.
    authMode: 'subscription',
    askKey: prefill.askKey === true,
    remediationRounds: ['0', '1', '2'].includes(prefill.remediationRounds ?? '') ? prefill.remediationRounds! : '1',
  };
}

export const NewRun: React.FC<{ prefill?: RunPrefill }> = ({ prefill = {} }) => {
  const ctx = useAppCtx();
  const ui = useUi();
  const [values, setValues] = useState<Record<string, FieldValue>>(() => initialRunValues(prefill, ctx.defaults));
  const [slugTouched, setSlugTouched] = useState(Boolean(prefill.slug));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [askedApiKey, setAskedApiKey] = useState(false);

  const wantsApiKey = prefill.authMode === 'api-key' || ctx.defaults.authMode === 'api-key';
  // Deep link or config asked for api-key: confirm once on first render.
  React.useEffect(() => {
    if (wantsApiKey && !askedApiKey) {
      setAskedApiKey(true);
      ctx.confirm(`${API_KEY_WARNING}\n\nUse api-key mode for this run?`, () => set('authMode', 'api-key'), 'Billed per token');
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const set = (id: string, v: FieldValue) => {
    setValues((cur) => {
      const next = { ...cur, [id]: v };
      if (id === 'client' && !slugTouched && typeof v === 'string') next.slug = v.trim() ? slugify(v) : '';
      return next;
    });
    if (id === 'slug') setSlugTouched(true);
    if (errors[id]) setErrors((e) => ({ ...e, [id]: '' }));
  };

  const onChange = (id: string, v: FieldValue) => {
    if (id === 'authMode' && v === 'api-key' && values.authMode !== 'api-key') {
      ctx.confirm(`${API_KEY_WARNING}\n\nSwitch this run to api-key mode?`, () => set('authMode', 'api-key'), 'Billed per token');
      return;
    }
    set(id, v);
  };

  const backends = ctx.defaults.backends.includes(String(values.backend))
    ? ctx.defaults.backends
    : [...ctx.defaults.backends, String(values.backend)];

  const fields: FieldDef[] = [
    { kind: 'section', label: 'Client' },
    { kind: 'text', id: 'client', label: 'Client legal name', required: true, hint: 'The registered legal name, e.g. "Northwind Ceramics plc".' },
    { kind: 'text', id: 'slug', label: 'Run slug', required: true, hint: 'Run directory name. Follows the client name until you edit it.' },
    { kind: 'text', id: 'commonName', label: 'Common name', placeholder: 'auto' },
    { kind: 'text', id: 'ticker', label: 'Ticker', placeholder: 'auto-detect' },
    { kind: 'text', id: 'vertical', label: 'Vertical', placeholder: 'auto-detect' },
    { kind: 'text', id: 'geography', label: 'Primary geography', placeholder: 'auto-detect' },
    { kind: 'text', id: 'asOf', label: 'Research as of', placeholder: 'today (YYYY-MM-DD)' },
    { kind: 'section', label: 'Pursuit inputs' },
    {
      kind: 'choice', id: 'capabilityPack', label: 'Capability pack', options: ATTACH,
      hint: 'Without it every organization capability claim renders [INTERNAL: validate with practice].',
    },
    {
      kind: 'choice', id: 'inputSheet', label: 'Input sheet', options: ATTACH,
      hint: 'Without it win probability, account revenue, relationship strength and stakeholder access render [INTERNAL REQUIRED].',
    },
    { kind: 'text', id: 'accountContext', label: 'Account context', placeholder: 'none' },
    { kind: 'text', id: 'relationship', label: 'Relationship', placeholder: 'none' },
    { kind: 'text', id: 'objectives', label: 'Objectives', placeholder: 'none' },
    { kind: 'section', label: 'Engine' },
    { kind: 'choice', id: 'backend', label: 'Backend', options: backends, hint: 'workflow runs on Claude Code (subscription); see the Backends screen for readiness.' },
    { kind: 'choice', id: 'tier', label: 'Tier', options: TIERS, labels: TIER_LABELS },
    {
      kind: 'choice', id: 'authMode', label: 'Auth mode', options: AUTH_MODES,
      hint: 'subscription runs on your Claude plan. api-key is billed per token and asks for confirmation.',
    },
    ...(values.authMode === 'api-key'
      ? [{ kind: 'bool', id: 'askKey', label: 'Prompt for key', hint: 'Prompt for any key missing from the environment. The key is never stored.' } as FieldDef]
      : []),
    {
      kind: 'choice', id: 'remediationRounds', label: 'Remediation rounds', options: ['0', '1', '2'],
      hint: 'P7R: route verification BLOCKERs back to their owning agents and re-verify. 0 disables.',
    },
    { kind: 'button', id: 'start', label: 'Start run' },
  ];

  const submit = () => {
    const e: Record<string, string> = {};
    const client = String(values.client ?? '').trim();
    const slug = String(values.slug ?? '').trim();
    if (!client) e.client = 'client legal name is required';
    if (!slug) e.slug = 'run slug is required';
    else if (!/^[A-Za-z0-9._-]+$/.test(slug)) e.slug = 'use letters, digits, dot, dash or underscore';
    const asOf = String(values.asOf ?? '').trim();
    if (asOf && !/^\d{4}-\d{2}-\d{2}$/.test(asOf)) e.asOf = 'use YYYY-MM-DD';
    setErrors(e);
    if (Object.keys(e).length) {
      ctx.toast('fix the highlighted fields', 'err');
      return;
    }
    if (ctx.run.active) {
      ctx.toast('a run is already in progress - see Live (3)', 'warn');
      return;
    }
    const s = (k: string) => {
      const v = values[k];
      return typeof v === 'string' && v.trim() ? v.trim() : undefined;
    };
    const params: RunParams = {
      client,
      slug,
      backend: s('backend'),
      tier: s('tier'),
      asOf: s('asOf'),
      commonName: s('commonName'),
      ticker: s('ticker'),
      vertical: s('vertical'),
      geography: s('geography'),
      capabilityPack: s('capabilityPack'),
      inputSheet: s('inputSheet'),
      accountContext: s('accountContext'),
      relationship: s('relationship'),
      objectives: s('objectives'),
      authMode: s('authMode'),
      askKey: values.authMode === 'api-key' && values.askKey === true,
      remediationRounds: Number(values.remediationRounds ?? 1),
    };
    if (ctx.run.start(params)) ctx.go('live');
  };

  return (
    <Panel
      title="New dossier"
      icon="newRun"
      focused
      right={<AuthBadge mode={String(values.authMode)} />}
    >
      <Form
        fields={fields}
        values={values}
        onChange={onChange}
        onSubmit={submit}
        errors={errors}
        labelWidth={ui.narrow ? 18 : 22}
        maxRows={Math.max(8, ui.height - 12)}
      />
      <Box marginTop={1}>
        <Txt dim>up/down move  enter edit/toggle  left/right cycle  esc cancel edit</Txt>
      </Box>
    </Panel>
  );
};
