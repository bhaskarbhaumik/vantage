// App-wide context: engine bridge, navigation, key routing, toasts and the run/export sessions.
import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import type { Key } from 'ink';
import type { Defaults, JsonObject } from '../lib/config.js';
import type { Bridge, ExportParams, Res, RunParams } from '../lib/engine.js';
import type { ExportState } from '../lib/exportState.js';
import type { RunState } from '../lib/runState.js';
import type { Tone } from '../lib/theme.js';

export type ScreenId =
  | 'home' | 'run' | 'live' | 'runs' | 'runDetail' | 'export' | 'doctor' | 'backends' | 'config';

export interface Route {
  screen: ScreenId;
  params?: Record<string, unknown>;
}

// Returns true when the key was handled, so the global bindings must not see it.
export type KeyHandler = (input: string, key: Key) => boolean | void;

export interface RunSession {
  state: RunState;
  params: RunParams | null;
  active: boolean;
  start(p: RunParams): boolean;
  cancel(): void;
}

export interface ExportSession {
  state: ExportState;
  params: ExportParams | null;
  active: boolean;
  start(p: ExportParams): boolean;
  cancel(): void;
  reset(): void;
}

export interface AppCtx {
  bridge: Bridge;
  defaults: Defaults;
  localConfig: JsonObject;
  tuiVersion: string;
  route: Route;
  // True while the help overlay or a confirmation is open: widgets with their own input pause.
  modal: boolean;
  go(screen: ScreenId, params?: Record<string, unknown>): void;
  back(): void;
  pushKeys(h: KeyHandler): () => void;
  toast(message: string, tone?: Tone): void;
  confirm(message: string, onYes: () => void, title?: string): void;
  quit(): void;
  run: RunSession;
  exp: ExportSession;
}

export const AppContext = createContext<AppCtx | null>(null);

export function useAppCtx(): AppCtx {
  const c = useContext(AppContext);
  if (!c) throw new Error('AppContext missing');
  return c;
}

// Register a key handler for the lifetime of the component; the latest-mounted handler wins.
export function useKeys(fn: KeyHandler): void {
  const ctx = useAppCtx();
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => ctx.pushKeys((i, k) => ref.current(i, k)), []); // eslint-disable-line react-hooks/exhaustive-deps
}

export interface AsyncState<T> {
  loading: boolean;
  data: T | null;
  error: string | null;
  reload(): void;
}

// Load once on mount (and on reload) from a Res-returning engine call.
export function useEngine<T>(fn: () => Promise<Res<T>>, deps: unknown[] = []): AsyncState<T> {
  const [state, setState] = useState<{ loading: boolean; data: T | null; error: string | null }>({
    loading: true,
    data: null,
    error: null,
  });
  const [nonce, setNonce] = useState(0);
  useEffect(() => {
    let alive = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((r) => {
        if (!alive) return;
        setState(r.ok ? { loading: false, data: r.data, error: null } : { loading: false, data: null, error: r.error });
      })
      .catch((e: unknown) => {
        if (alive) setState({ loading: false, data: null, error: String(e) });
      });
    return () => {
      alive = false;
    };
  }, [nonce, ...deps]); // eslint-disable-line react-hooks/exhaustive-deps
  return { ...state, reload: () => setNonce((n) => n + 1) };
}
