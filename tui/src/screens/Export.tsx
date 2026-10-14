// Export wizard: choose formats and options, then follow live progress and the artifact list.
import fs from 'node:fs';
import React, { useState } from 'react';
import { Box } from 'ink';
import { useAppCtx, useKeys } from '../components/context.js';
import { Form, type FieldDef, type FieldValue } from '../components/Form.js';
import { Bar, Field, Line, Panel, Spin, Txt, useIcon, useUi } from '../components/ui.js';
import type { ExportPrefill } from '../lib/args.js';
import { AUTHORING, CHARTS, DEPTHS, DIAGRAMS, EXPORT_FORMATS, ILLUSTRATIONS, SITE_MODES, type Defaults } from '../lib/config.js';
import type { ExportParams } from '../lib/engine.js';
import { type ExportState, exportProgress } from '../lib/exportState.js';
import { bytes, elapsed, pad, shortPath, truncateStart } from '../lib/format.js';
import type { IconName } from '../lib/icons.js';
import { copyText, openPath } from '../lib/system.js';

const FORMAT_ICON: Record<string, IconName> = { pptx: 'pptx', docx: 'docx', pdf: 'pdf', html: 'html' };

export function initialExportValues(p: ExportPrefill, d: Defaults, dossier?: string): Record<string, FieldValue> {
  const e = d.export;
  const formats = (p.formats ?? e.formats).filter((f) => EXPORT_FORMATS.includes(f));
  return {
    dossier: dossier ?? p.dossier ?? '',
    formats: formats.length ? formats : EXPORT_FORMATS,
    depth: p.depth && DEPTHS.includes(p.depth) ? p.depth : e.depth,
    siteMode: p.siteMode && SITE_MODES.includes(p.siteMode) ? p.siteMode : e.siteMode,
    authoring: p.authoring && AUTHORING.includes(p.authoring) ? p.authoring : e.authoring,
    brand: p.brand ?? e.brand,
    classification: p.classification ?? e.classification,
    outDir: p.outDir ?? e.outDir,
    clientLogo: p.clientLogo ?? e.clientLogo,
    hIcons: e.helpers.icons,
    hBrand: e.helpers.brand,
    hStock: e.helpers.stockImages,
    hDiagrams: e.helpers.diagrams,
    hIllustrations: e.helpers.illustrations,
    hCharts: e.helpers.charts,
  };
}

// Helper settings that differ from the configured defaults, as engine `--helper key=value` pairs.
export function helperOverrides(v: Record<string, FieldValue>, d: Defaults): Record<string, string> {
  const h = d.export.helpers;
  const out: Record<string, string> = {};
  const onOff = (b: FieldValue) => (b === true ? 'on' : 'off');
  if (v.hIcons !== h.icons) out.icons = onOff(v.hIcons);
  if (v.hBrand !== h.brand) out.brand = onOff(v.hBrand);
  if (v.hStock !== h.stockImages) out.stock_images = onOff(v.hStock);
  if (v.hDiagrams !== h.diagrams) out.diagrams = String(v.hDiagrams);
  if (v.hIllustrations !== h.illustrations) out.illustrations = String(v.hIllustrations);
  if (v.hCharts !== h.charts) out.charts = String(v.hCharts);
  return out;
}

export const ExportProgress: React.FC<{ state: ExportState; now: number }> = ({ state, now }) => {
  const ui = useUi();
  const ic = useIcon();
  const frac = exportProgress(state);
  const running = state.status === 'running';
  const pathW = Math.max(20, ui.width - (ui.narrow ? 36 : 66));
  return (
    <Box flexDirection="column">
      <Box>
        <Bar fraction={state.status === 'done' ? 1 : frac} width={Math.max(10, Math.min(40, ui.width - 40))} tone={state.status === 'failed' ? 'err' : 'accent'} />
        <Txt> {Math.round((state.status === 'done' ? 1 : frac) * 100)}%  </Txt>
        <Txt bold tone={state.status === 'done' ? 'ok' : state.status === 'running' ? 'info' : 'err'}>
          {state.status}
        </Txt>
        <Txt dim>  {elapsed((state.endedAt ?? now) - (state.startedAt ?? now))}</Txt>
      </Box>
      <Box flexDirection={ui.narrow ? 'column' : 'row'} marginTop={1}>
        <Box flexDirection="column" width={ui.narrow ? undefined : 30}>
          {state.stages.map((s) => (
            <Box key={s.name}>
              {s.status === 'running' ? (
                <Spin />
              ) : (
                <Txt tone={s.status === 'done' ? 'ok' : s.status === 'error' ? 'err' : 'muted'}>
                  {ic(s.status === 'done' ? 'ok' : s.status === 'error' ? 'fail' : s.status === 'skipped' ? 'skipped' : 'pending')}
                </Txt>
              )}
              <Txt bold={s.status === 'running'} dim={s.status === 'pending' || s.status === 'skipped'}> {s.name}</Txt>
            </Box>
          ))}
        </Box>
        <Box flexDirection="column" flexGrow={1}>
          <Txt bold>Artifacts ({state.artifacts.length})</Txt>
          {state.artifacts.length === 0 ? <Txt dim>{running ? 'waiting for the first file...' : 'none'}</Txt> : null}
          {state.artifacts.map((a) => (
            <Line key={a.path} pointer={false}>
              <Txt tone="accent">{ic(FORMAT_ICON[a.format] ?? 'file')} </Txt>
              <Txt bold>{pad(a.format, 5)}</Txt>
              <Txt> {truncateStart(shortPath(a.path), pathW)}</Txt>
              <Txt dim>
                {'  '}
                {bytes(a.bytes)}
                {a.slides ? `  ${a.slides} slides` : ''}
                {a.pages ? `  ${a.pages} pages` : ''}
              </Txt>
            </Line>
          ))}
        </Box>
      </Box>
      {state.warnings.length ? (
        <Box flexDirection="column" marginTop={1}>
          {state.warnings.slice(-6).map((w, i) => (
            <Txt key={i} tone="warn" wrap="truncate">
              {ic('warn')} {w}
            </Txt>
          ))}
        </Box>
      ) : null}
      {state.errors.length ? (
        <Box flexDirection="column" marginTop={1}>
          {state.errors.slice(-4).map((e, i) => (
            <Txt key={i} tone="err" wrap="wrap">
              {ic('error')} {e}
            </Txt>
          ))}
        </Box>
      ) : null}
      {state.status === 'done' ? (
        <Box flexDirection="column" marginTop={1}>
          {state.outDir ? (
            <Field label="out dir">
              <Txt bold>{shortPath(state.outDir)}</Txt>
            </Field>
          ) : null}
          {state.manifest ? (
            <Field label="manifest">
              <Txt>{shortPath(state.manifest)}</Txt>
            </Field>
          ) : null}
          {Object.keys(state.plans).length ? (
            <Field label="plans">
              <Txt dim>
                {Object.entries(state.plans)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join('  ')}
              </Txt>
            </Field>
          ) : null}
        </Box>
      ) : null}
    </Box>
  );
};

export const Export: React.FC<{ prefill?: ExportPrefill; dossier?: string }> = ({ prefill = {}, dossier }) => {
  const ctx = useAppCtx();
  const ui = useUi();
  const [values, setValues] = useState<Record<string, FieldValue>>(() => initialExportValues(prefill, ctx.defaults, dossier));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [now, setNow] = useState(Date.now());
  const st = ctx.exp.state;
  const showProgress = st.status !== 'idle';

  React.useEffect(() => {
    if (st.status !== 'running') return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [st.status]);

  const onChange = (id: string, v: FieldValue) => {
    if (id === 'hIllustrations' && v === 'napkin') {
      ctx.confirm('Napkin illustrations spend Napkin credits on your account. Turn them on for this export?', () =>
        setValues((cur) => ({ ...cur, hIllustrations: 'napkin' })), 'Paid helper');
      return;
    }
    if (id === 'authoring' && v === 'agents') {
      ctx.toast('agents authoring calls Claude to write the plans (uses your configured auth mode)', 'info');
    }
    setValues((cur) => ({ ...cur, [id]: v }));
    if (errors[id]) setErrors((e) => ({ ...e, [id]: '' }));
  };

  const resolveDossier = async (raw: string): Promise<string | null> => {
    const v = raw.trim();
    if (!v) return null;
    if (fs.existsSync(v.replace(/^~(?=\/)/, process.env.HOME ?? '~'))) return v.replace(/^~(?=\/)/, process.env.HOME ?? '~');
    if (/^[A-Za-z0-9._-]+$/.test(v)) {
      const r = await ctx.bridge.runsShow(v);
      if (r.ok) return r.data.dossier ?? r.data.run_dir;
    }
    return v;
  };

  const submit = async () => {
    if (busy) return;
    const e: Record<string, string> = {};
    const formats = Array.isArray(values.formats) ? values.formats : [];
    if (!String(values.dossier ?? '').trim()) e.dossier = 'a run slug, run directory or *-vantage.md path is required';
    if (!formats.length) e.formats = 'pick at least one format';
    setErrors(e);
    if (Object.keys(e).length) return;
    if (ctx.exp.active) {
      ctx.toast('an export is already running', 'warn');
      return;
    }
    setBusy(true);
    const path = await resolveDossier(String(values.dossier));
    setBusy(false);
    if (!path) return;
    const s = (k: string) => (typeof values[k] === 'string' && String(values[k]).trim() ? String(values[k]).trim() : undefined);
    const params: ExportParams = {
      dossier: path,
      formats,
      depth: s('depth'),
      siteMode: s('siteMode'),
      authoring: s('authoring'),
      outDir: s('outDir'),
      classification: s('classification'),
      brand: s('brand'),
      clientLogo: values.clientLogo === true,
      helpers: helperOverrides(values, ctx.defaults),
    };
    ctx.exp.start(params);
  };

  useKeys((input) => {
    if (!showProgress) return false;
    if (input === 'n' && st.status !== 'running') {
      ctx.exp.reset();
      return true;
    }
    if (input === 'x' && st.status === 'running') {
      ctx.confirm('Stop this export?', () => ctx.exp.cancel(), 'Cancel export');
      return true;
    }
    const target = st.outDir ?? st.artifacts[0]?.path;
    if (input === 'o' && target) {
      void openPath(target).then((ok) => ctx.toast(ok ? `opened ${shortPath(target)}` : 'could not open a file manager', ok ? 'ok' : 'warn'));
      return true;
    }
    if (input === 'c' && target) {
      void copyText(target).then((ok) => ctx.toast(ok ? `copied ${shortPath(target)}` : `no clipboard tool - path: ${target}`, ok ? 'ok' : 'warn'));
      return true;
    }
    return false;
  });

  if (showProgress) {
    return (
      <Panel
        title={`Export ${ctx.exp.params ? shortPath(ctx.exp.params.dossier) : ''}`}
        icon="export"
        focused={st.status === 'running'}
      >
        <ExportProgress state={st} now={now} />
        <Box marginTop={1}>
          <Txt dim>
            {st.status === 'running' ? 'x stop export' : 'n new export  o open folder  c copy path'}
          </Txt>
        </Box>
      </Panel>
    );
  }

  const fields: FieldDef[] = [
    { kind: 'section', label: 'Source' },
    { kind: 'text', id: 'dossier', label: 'Dossier', required: true, hint: 'A run slug, a run directory, or a *-vantage.md file.' },
    { kind: 'section', label: 'Output' },
    { kind: 'multi', id: 'formats', label: 'Formats', options: EXPORT_FORMATS, hint: 'left/right pick a format, space toggles it. pdf is converted from the docx.' },
    { kind: 'choice', id: 'depth', label: 'Depth', options: DEPTHS, hint: 'exec: headline pages only. full: every section and appendix.' },
    { kind: 'choice', id: 'siteMode', label: 'HTML site mode', options: SITE_MODES },
    { kind: 'choice', id: 'authoring', label: 'Authoring', options: AUTHORING, hint: 'deterministic maps the dossier directly; agents lets Claude author the plans.' },
    { kind: 'text', id: 'outDir', label: 'Output directory', placeholder: '<run dir>/exports' },
    { kind: 'section', label: 'Branding' },
    { kind: 'text', id: 'brand', label: 'Brand domain', placeholder: 'none (neutral theme)', hint: 'The pursuing organization\'s domain; its logo and palette theme the output.' },
    { kind: 'text', id: 'classification', label: 'Classification', hint: 'Marking printed on every page, slide and screen.' },
    { kind: 'bool', id: 'clientLogo', label: 'Client logo' },
    { kind: 'section', label: 'Helpers' },
    { kind: 'bool', id: 'hIcons', label: 'Icons' },
    { kind: 'bool', id: 'hBrand', label: 'Brand fetch' },
    { kind: 'bool', id: 'hStock', label: 'Stock images' },
    { kind: 'choice', id: 'hDiagrams', label: 'Diagrams', options: DIAGRAMS },
    { kind: 'choice', id: 'hIllustrations', label: 'Illustrations', options: ILLUSTRATIONS, hint: 'napkin spends Napkin credits and asks first.' },
    { kind: 'choice', id: 'hCharts', label: 'Charts', options: CHARTS },
    { kind: 'button', id: 'start', label: busy ? 'Resolving...' : 'Start export' },
  ];

  return (
    <Panel title="Export" icon="export" focused>
      <Form
        fields={fields}
        values={values}
        onChange={onChange}
        onSubmit={() => void submit()}
        errors={errors}
        labelWidth={ui.narrow ? 16 : 20}
        maxRows={Math.max(8, ui.height - 12)}
      />
    </Panel>
  );
};

export const EXPORT_KEYS: [string, string][] = [
  ['up/down', 'move between fields'],
  ['left/right', 'cycle a choice / pick a format'],
  ['space', 'toggle'],
  ['enter', 'edit text / start'],
  ['x', 'stop a running export'],
  ['n', 'new export after one finishes'],
  ['o / c', 'open / copy the output folder'],
];
