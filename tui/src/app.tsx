// App shell: header and tab bar, screen router, overlays (help, confirm), toasts, global keys,
// and the run/export sessions that outlive screen changes.
import React, { useCallback, useEffect, useMemo, useReducer, useRef, useState } from 'react';
import { Box, type Key, useApp, useInput } from 'ink';
import {
  AppContext,
  type AppCtx,
  type ExportSession,
  type KeyHandler,
  type Route,
  type RunSession,
  type ScreenId,
} from './components/context.js';
import { GLOBAL_KEYS, Help } from './components/Help.js';
import { AuthBadge, KeyHints, Panel, Spin, Txt, UiProvider, useIcon, useUi } from './components/ui.js';
import type { CliArgs } from './lib/args.js';
import { getPath, type Defaults, type JsonObject } from './lib/config.js';
import type { Bridge, ExportParams, RunEvent, RunParams, Stream } from './lib/engine.js';
import { exportReducer, initialExportState } from './lib/exportState.js';
import type { IconName } from './lib/icons.js';
import { initialRunState, runReducer } from './lib/runState.js';
import type { Tone, UiPrefs } from './lib/theme.js';
import { BACKENDS_KEYS, Backends, DOCTOR_KEYS, Doctor } from './screens/Doctor.js';
import { CONFIG_KEYS, Config } from './screens/Config.js';
import { EXPORT_KEYS, Export } from './screens/Export.js';
import { Home } from './screens/Home.js';
import { LIVE_KEYS, Live } from './screens/Live.js';
import { NewRun } from './screens/NewRun.js';
import { DETAIL_KEYS, RUNS_KEYS, RunDetail, Runs } from './screens/Runs.js';

export const TABS: { id: ScreenId; label: string; icon: IconName }[] = [
  { id: 'home', label: 'Home', icon: 'home' },
  { id: 'run', label: 'New', icon: 'newRun' },
  { id: 'live', label: 'Live', icon: 'live' },
  { id: 'runs', label: 'Runs', icon: 'runs' },
  { id: 'export', label: 'Export', icon: 'export' },
  { id: 'doctor', label: 'Doctor', icon: 'doctor' },
  { id: 'backends', label: 'Backends', icon: 'backends' },
  { id: 'config', label: 'Config', icon: 'config' },
];

const SCREEN_KEYS: Record<ScreenId, { title: string; keys: [string, string][]; short: [string, string][] }> = {
  home: { title: 'Home', keys: [['up/down', 'move'], ['enter', 'open the highlighted action']], short: [['enter', 'open'], ['1-8', 'screens']] },
  run: {
    title: 'New dossier',
    keys: [['up/down', 'move between fields'], ['enter', 'edit text / toggle / start'], ['left/right space', 'cycle a choice'], ['backspace', 'clear a text field'], ['esc', 'cancel an edit']],
    short: [['up/down', 'move'], ['enter', 'edit'], ['left/right', 'cycle']],
  },
  live: { title: 'Live run', keys: LIVE_KEYS, short: [['p', 'pause'], ['l', 'log'], ['/', 'filter'], ['c', 'cancel'], ['q', 'quit']] },
  runs: { title: 'Runs', keys: RUNS_KEYS, short: [['enter', 'open'], ['s', 'sort'], ['/', 'filter'], ['e', 'export'], ['o', 'open dir'], ['c', 'copy']] },
  runDetail: { title: 'Run detail', keys: DETAIL_KEYS, short: [['e', 'export'], ['o', 'open dir'], ['c', 'copy path'], ['esc', 'back']] },
  export: { title: 'Export', keys: EXPORT_KEYS, short: [['up/down', 'move'], ['space', 'toggle'], ['enter', 'edit/start']] },
  doctor: { title: 'Doctor', keys: DOCTOR_KEYS, short: [['r', 're-run'], ['f', 'problems only']] },
  backends: { title: 'Backends', keys: BACKENDS_KEYS, short: [['enter', 'new run here'], ['r', 'reload']] },
  config: { title: 'Config', keys: CONFIG_KEYS, short: [['enter', 'expand/edit'], ['space', 'toggle'], ['r', 'reload']] },
};

function footerHints(short: [string, string][]): [string, string][] {
  const out = [...short];
  for (const h of [['?', 'help'], ['esc', 'back'], ['q', 'quit']] as [string, string][]) {
    if (!out.some(([k]) => k === h[0])) out.push(h);
  }
  return out;
}

function tabOf(screen: ScreenId): ScreenId {
  return screen === 'runDetail' ? 'runs' : screen;
}

export function initialRoutes(args: Pick<CliArgs, 'screen' | 'run' | 'exportOpts' | 'slug'>): Route[] {
  switch (args.screen) {
    case 'run':
      return [{ screen: 'run', params: { ...args.run } }];
    case 'runs':
      return args.slug ? [{ screen: 'runs' }, { screen: 'runDetail', params: { slug: args.slug } }] : [{ screen: 'runs' }];
    case 'export':
      return [{ screen: 'export', params: { prefill: args.exportOpts } }];
    case 'live':
    case 'doctor':
    case 'backends':
    case 'config':
      return [{ screen: args.screen }];
    default:
      return [{ screen: 'home' }];
  }
}

interface Toast {
  id: number;
  message: string;
  tone: Tone;
}

interface Confirm {
  title: string;
  message: string;
  onYes: () => void;
}

export interface AppProps {
  bridge: Bridge;
  args: Pick<CliArgs, 'screen' | 'run' | 'exportOpts' | 'slug' | 'help'>;
  prefs: UiPrefs;
  defaults: Defaults;
  localConfig: JsonObject;
  tuiVersion: string;
  width?: number;
  height?: number;
  onQuit?: () => void;
}

// Coalesce bursts of engine events into one state update every few frames.
function useBatcher(dispatch: (events: RunEvent[]) => void, ms = 60) {
  const queue = useRef<RunEvent[]>([]);
  const timer = useRef<NodeJS.Timeout | null>(null);
  const flush = useCallback(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    if (queue.current.length) {
      const evs = queue.current;
      queue.current = [];
      dispatch(evs);
    }
  }, [dispatch]);
  const push = useCallback(
    (ev: RunEvent) => {
      queue.current.push(ev);
      if (!timer.current) timer.current = setTimeout(flush, ms);
    },
    [flush, ms],
  );
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);
  return { push, flush };
}

const Header: React.FC<{ active: ScreenId; engineVersion: string | null; auth: string; running: boolean; tuiVersion: string }> = ({
  active,
  engineVersion,
  auth,
  running,
  tuiVersion,
}) => {
  const ui = useUi();
  const ic = useIcon();
  const tab = tabOf(active);
  return (
    <Box flexDirection="column">
      <Box justifyContent="space-between">
        <Box>
          <Txt tone="accent" bold>
            {ic('logo')} Vantage{ic('tm')}
          </Txt>
          {ui.width >= 120 ? <Txt dim>  Verified Account Navigator: Targeting, Analysis &amp; GTM Engine</Txt> : null}
        </Box>
        <Box>
          {running ? (
            <Box marginRight={1}>
              <Spin />
              <Txt tone="info"> run</Txt>
            </Box>
          ) : null}
          <AuthBadge mode={auth} />
          <Txt dim>  {engineVersion ? `engine ${engineVersion}` : `tui ${tuiVersion}`}</Txt>
        </Box>
      </Box>
      <Box flexWrap="wrap">
        {TABS.map((t, i) => {
          const on = t.id === tab;
          return (
            <Box key={t.id} marginRight={ui.narrow ? 1 : 2}>
              <Txt tone={on ? 'accent' : 'muted'} bold={on} underline={on}>
                {i + 1}
                {ui.prefs.icons === 'ascii' ? ':' : ' '}
                {ic(t.icon)}
                {ui.narrow && !on ? '' : ` ${t.label}`}
              </Txt>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
};

const AppInner: React.FC<AppProps> = (props) => {
  const { bridge, args, defaults, localConfig, tuiVersion, onQuit } = props;
  const { exit } = useApp();
  const ui = useUi();
  const [routes, setRoutes] = useState<Route[]>(() => initialRoutes(args));
  const [help, setHelp] = useState(Boolean(args.help));
  const [confirm, setConfirm] = useState<Confirm | null>(null);
  const [toast, setToast] = useState<Toast | null>(null);
  const [engineVersion, setEngineVersion] = useState<string | null>(null);
  const handlers = useRef<KeyHandler[]>([]);
  const route = routes[routes.length - 1];

  // --- sessions -------------------------------------------------------------------------------
  const [runState, dispatchRun] = useReducer(runReducer, undefined, initialRunState);
  const [runParams, setRunParams] = useState<RunParams | null>(null);
  const runStream = useRef<Stream | null>(null);
  const runBatch = useBatcher(useCallback((events: RunEvent[]) => dispatchRun({ kind: 'batch', events }), []));

  const [expState, dispatchExp] = useReducer(exportReducer, undefined, () => initialExportState());
  const [expParams, setExpParams] = useState<ExportParams | null>(null);
  const expStream = useRef<Stream | null>(null);
  const expBatch = useBatcher(useCallback((events: RunEvent[]) => dispatchExp({ kind: 'batch', events }), []));

  const run: RunSession = {
    state: runState,
    params: runParams,
    active: runState.status === 'running',
    start: (p) => {
      if (runStream.current) return false;
      setRunParams(p);
      dispatchRun({ kind: 'start', client: p.client });
      const s = bridge.startRun(p, runBatch.push);
      runStream.current = s;
      void s.done.then((o) => {
        runBatch.flush();
        dispatchRun({ kind: 'result', ...o });
        runStream.current = null;
      });
      return true;
    },
    cancel: () => runStream.current?.cancel(),
  };

  const exp: ExportSession = {
    state: expState,
    params: expParams,
    active: expState.status === 'running',
    start: (p) => {
      if (expStream.current) return false;
      setExpParams(p);
      dispatchExp({ kind: 'start', formats: p.formats });
      const s = bridge.startExport(p, expBatch.push);
      expStream.current = s;
      void s.done.then((o) => {
        expBatch.flush();
        dispatchExp({ kind: 'result', ...o });
        expStream.current = null;
      });
      return true;
    },
    cancel: () => expStream.current?.cancel(),
    reset: () => {
      if (!expStream.current) dispatchExp({ kind: 'reset' });
    },
  };

  useEffect(() => {
    let alive = true;
    void bridge.version().then((r) => {
      if (alive && r.ok) setEngineVersion(r.data.version);
    });
    return () => {
      alive = false;
    };
  }, [bridge]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast((cur) => (cur?.id === toast.id ? null : cur)), 4000);
    return () => clearTimeout(t);
  }, [toast]);

  // --- navigation and app API ------------------------------------------------------------------
  const quit = () => {
    runStream.current?.cancel();
    expStream.current?.cancel();
    onQuit?.();
    exit();
  };

  const go = (screen: ScreenId, params?: Record<string, unknown>) => {
    setHelp(false);
    setRoutes((rs) => {
      const top = rs[rs.length - 1];
      const next = { screen, params };
      if (top.screen === screen && !params) return rs;
      return [...rs.slice(-19), next];
    });
  };

  const back = () => setRoutes((rs) => (rs.length > 1 ? rs.slice(0, -1) : rs));

  const ctx: AppCtx = {
    bridge,
    defaults,
    localConfig,
    tuiVersion,
    route,
    modal: help || confirm !== null,
    go,
    back,
    pushKeys: (h) => {
      handlers.current.push(h);
      return () => {
        handlers.current = handlers.current.filter((x) => x !== h);
      };
    },
    toast: (message, tone = 'info') => setToast({ id: Date.now() + Math.random(), message, tone }),
    confirm: (message, onYes, title = 'Confirm') => setConfirm({ title, message, onYes }),
    quit,
    run,
    exp,
  };

  // --- global keys -----------------------------------------------------------------------------
  const onKey = (input: string, key: Key) => {
    if (key.ctrl && input === 'c') {
      quit();
      return;
    }
    if (confirm) {
      if (input === 'y' || input === 'Y' || key.return) {
        const c = confirm;
        setConfirm(null);
        c.onYes();
      } else if (input === 'n' || input === 'N' || key.escape || input === 'q') {
        setConfirm(null);
      }
      return;
    }
    if (help) {
      if (key.escape || input === '?' || input === 'q') setHelp(false);
      return;
    }
    // Screen handlers, newest first; a handler returning true consumes the key.
    for (let i = handlers.current.length - 1; i >= 0; i--) {
      if (handlers.current[i](input, key)) return;
    }
    if (input === '?') {
      setHelp(true);
      return;
    }
    if (key.tab) {
      const idx = TABS.findIndex((t) => t.id === tabOf(route.screen));
      const n = TABS.length;
      go(TABS[(idx + (key.shift ? -1 : 1) + n) % n].id);
      return;
    }
    if (/^[1-8]$/.test(input)) {
      go(TABS[Number(input) - 1].id);
      return;
    }
    if (key.escape) {
      back();
      return;
    }
    if (input === 'q') {
      if (runState.status === 'running' || expState.status === 'running') {
        ctx.confirm('A run or export is in progress. Quit and stop the engine?', quit, 'Quit');
      } else {
        quit();
      }
    }
  };
  useInput(onKey);

  const auth = String(runParams?.authMode && runState.status === 'running' ? runParams.authMode : getPath(localConfig, 'auth.mode') ?? defaults.authMode);
  const sk = SCREEN_KEYS[route.screen];
  const p = route.params ?? {};

  const screen = useMemo(() => {
    switch (route.screen) {
      case 'home':
        return <Home />;
      case 'run':
        return <NewRun prefill={p} />;
      case 'live':
        return <Live />;
      case 'runs':
        return <Runs />;
      case 'runDetail':
        return <RunDetail slug={String(p.slug ?? '')} />;
      case 'export':
        return <Export prefill={(p.prefill as CliArgs['exportOpts']) ?? {}} dossier={typeof p.dossier === 'string' ? p.dossier : undefined} />;
      case 'doctor':
        return <Doctor />;
      case 'backends':
        return <Backends />;
      case 'config':
        return <Config />;
    }
  }, [route]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <AppContext.Provider value={ctx}>
      <Box flexDirection="column" width={ui.width}>
        <Header active={route.screen} engineVersion={engineVersion} auth={auth} running={runState.status === 'running'} tuiVersion={tuiVersion} />
        {confirm ? (
          <Panel title={confirm.title} icon="warn" tone="warn" focused>
            {confirm.message.split('\n').map((l, i) => (
              <Txt key={i} wrap="wrap">
                {l}
              </Txt>
            ))}
            <Box marginTop={1}>
              <KeyHints hints={[['y', 'yes'], ['n / esc', 'no']]} />
            </Box>
          </Panel>
        ) : null}
        {help ? <Help screenTitle={sk.title} screenKeys={sk.keys} /> : null}
        <Box display={help ? 'none' : 'flex'} flexDirection="column" key={`${routes.length}-${route.screen}`}>
          {screen}
        </Box>
        <Box justifyContent="space-between">
          <KeyHints hints={footerHints(sk.short)} />
        </Box>
        {toast ? (
          <Txt tone={toast.tone} wrap="truncate">
            {toast.message}
          </Txt>
        ) : null}
      </Box>
    </AppContext.Provider>
  );
};

export const App: React.FC<AppProps> = (props) => (
  <UiProvider prefs={props.prefs} width={props.width} height={props.height}>
    <AppInner {...props} />
  </UiProvider>
);

export { GLOBAL_KEYS };
