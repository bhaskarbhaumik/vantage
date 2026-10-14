// Local view of the configuration: shipped defaults merged with ~/.config/vantage/default.json.
// Used for form defaults and presentation preferences without waiting on the engine; the Config
// screen reads the engine's effective config (`vantage config show --json`) instead.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { repoRoot } from './engine.js';

export type Json = null | boolean | number | string | Json[] | { [k: string]: Json };
export type JsonObject = { [k: string]: Json };

export function userConfigPath(env: NodeJS.ProcessEnv = process.env): string {
  const base = env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config');
  return path.join(base, 'vantage', 'default.json');
}

function readJson(p: string): JsonObject | null {
  try {
    const v = JSON.parse(fs.readFileSync(p, 'utf8')) as Json;
    return v && typeof v === 'object' && !Array.isArray(v) ? v : null;
  } catch {
    return null;
  }
}

export function deepMerge(base: JsonObject, over: JsonObject): JsonObject {
  const out: JsonObject = { ...base };
  for (const [k, v] of Object.entries(over)) {
    const b = out[k];
    if (v && typeof v === 'object' && !Array.isArray(v) && b && typeof b === 'object' && !Array.isArray(b)) {
      out[k] = deepMerge(b, v);
    } else {
      out[k] = v;
    }
  }
  return out;
}

export function loadLocalConfig(env: NodeJS.ProcessEnv = process.env): JsonObject {
  const shipped = readJson(path.join(repoRoot(), 'config', 'default.json')) ?? {};
  const user = readJson(userConfigPath(env)) ?? {};
  return deepMerge(shipped, user);
}

export function getPath(obj: Json | undefined, dotted: string): Json | undefined {
  let cur: Json | undefined = obj;
  for (const part of dotted.split('.')) {
    if (!cur || typeof cur !== 'object' || Array.isArray(cur)) return undefined;
    cur = cur[part];
  }
  return cur;
}

function s(v: Json | undefined, fallback: string): string {
  return typeof v === 'string' && v.length ? v : fallback;
}

function b(v: Json | undefined, fallback: boolean): boolean {
  return typeof v === 'boolean' ? v : fallback;
}

export const ALL_BACKENDS = ['workflow', 'api', 'agent-sdk', 'langgraph', 'adk', 'crewai'];
export const TIERS = ['FULL_ANNEX', 'STANDARD', 'EXECUTIVE'];
export const AUTH_MODES = ['subscription', 'api-key'];
export const ATTACH = ['NOT_ATTACHED', 'ATTACHED'];
export const EXPORT_FORMATS = ['pptx', 'docx', 'pdf', 'html'];
export const DEPTHS = ['exec', 'standard', 'full'];
export const SITE_MODES = ['microsite', 'deck'];
export const AUTHORING = ['deterministic', 'agents'];
export const DIAGRAMS = ['auto', 'dgm', 'drawio', 'mermaid', 'none'];
export const ILLUSTRATIONS = ['none', 'napkin'];
export const CHARTS = ['matplotlib', 'plotly'];

export interface Defaults {
  backends: string[];
  backend: string;
  tier: string;
  authMode: string;
  capabilityPack: string;
  inputSheet: string;
  accountContext: string;
  relationship: string;
  objectives: string;
  export: {
    formats: string[];
    depth: string;
    siteMode: string;
    authoring: string;
    outDir: string;
    classification: string;
    brand: string;
    clientLogo: boolean;
    helpers: {
      icons: boolean;
      brand: boolean;
      stockImages: boolean;
      diagrams: string;
      illustrations: string;
      charts: string;
    };
  };
}

function noneToEmpty(v: string): string {
  return v === 'NONE' || v === 'AUTO-DETECT' ? '' : v;
}

export function defaultsFrom(cfg: JsonObject): Defaults {
  const avail = getPath(cfg, 'engine.available_backends');
  const formats = getPath(cfg, 'export.formats');
  return {
    backends: Array.isArray(avail) && avail.every((x) => typeof x === 'string')
      ? (avail as string[])
      : ALL_BACKENDS,
    backend: s(getPath(cfg, 'engine.backend'), 'workflow'),
    tier: s(getPath(cfg, 'engine.tier'), 'FULL_ANNEX'),
    authMode: s(getPath(cfg, 'auth.mode'), 'subscription'),
    capabilityPack: s(getPath(cfg, 'run_defaults.capability_pack'), 'NOT_ATTACHED'),
    inputSheet: s(getPath(cfg, 'run_defaults.account_team_input_sheet'), 'NOT_ATTACHED'),
    accountContext: noneToEmpty(s(getPath(cfg, 'run_defaults.account_context'), '')),
    relationship: noneToEmpty(s(getPath(cfg, 'run_defaults.known_relationship_context'), '')),
    objectives: noneToEmpty(s(getPath(cfg, 'run_defaults.strategic_pursuit_objectives'), '')),
    export: {
      formats: Array.isArray(formats) ? formats.filter((f): f is string => typeof f === 'string') : EXPORT_FORMATS,
      depth: s(getPath(cfg, 'export.depth'), 'standard'),
      siteMode: s(getPath(cfg, 'export.site_mode'), 'microsite'),
      authoring: s(getPath(cfg, 'export.authoring'), 'deterministic'),
      outDir: s(getPath(cfg, 'export.out_dir'), ''),
      classification: s(getPath(cfg, 'export.classification'), 'Confidential'),
      brand: s(getPath(cfg, 'export.brand'), ''),
      clientLogo: b(getPath(cfg, 'export.client_logo'), true),
      helpers: {
        icons: b(getPath(cfg, 'export.helpers.icons'), true),
        brand: b(getPath(cfg, 'export.helpers.brand'), true),
        stockImages: b(getPath(cfg, 'export.helpers.stock_images'), true),
        diagrams: s(getPath(cfg, 'export.helpers.diagrams'), 'auto'),
        illustrations: s(getPath(cfg, 'export.helpers.illustrations'), 'none'),
        charts: s(getPath(cfg, 'export.helpers.charts'), 'matplotlib'),
      },
    },
  };
}
