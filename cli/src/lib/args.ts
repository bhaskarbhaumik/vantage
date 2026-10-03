// Minimal argv parser: a leading subcommand + --flag value pairs.
export interface Parsed {
  subcommand?: string;
  flags: Record<string, string>;
}

export const PASSTHROUGH = new Set(['doctor', 'backends', 'config', 'auth', 'deploy', 'version']);

export function parseArgs(argv: string[]): Parsed {
  const rest = [...argv];
  let subcommand: string | undefined;
  if (rest.length && !rest[0].startsWith('-')) subcommand = rest.shift();
  const flags: Record<string, string> = {};
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = rest[i + 1];
      if (next !== undefined && !next.startsWith('--')) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = 'true';
      }
    }
  }
  return { subcommand, flags };
}
