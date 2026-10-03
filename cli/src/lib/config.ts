// Read the user config (~/.config/vantage/default.json) for TUI defaults.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export interface Defaults {
  backends: string[];
  backend: string;
  tier: string;
  authMode: string;
}

const FALLBACK: Defaults = {
  backends: ['workflow', 'api', 'agent-sdk', 'langgraph', 'adk', 'crewai'],
  backend: 'workflow',
  tier: 'FULL_ANNEX',
  authMode: 'subscription',
};

export function userConfigPath(): string {
  const base = process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config');
  return path.join(base, 'vantage', 'default.json');
}

export function loadDefaults(): Defaults {
  try {
    const j = JSON.parse(fs.readFileSync(userConfigPath(), 'utf8'));
    const eng = j.engine ?? {};
    const auth = j.auth ?? {};
    return {
      backends: Array.isArray(eng.available_backends) ? eng.available_backends : FALLBACK.backends,
      backend: eng.backend ?? FALLBACK.backend,
      tier: eng.tier ?? FALLBACK.tier,
      authMode: auth.mode ?? FALLBACK.authMode,
    };
  } catch {
    return FALLBACK;
  }
}
