// Desktop integration: open a folder in the file manager, copy text to the clipboard.
import { spawn } from 'node:child_process';

function run(cmd: string, args: string[], input?: string): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      const child = spawn(cmd, args, { stdio: [input === undefined ? 'ignore' : 'pipe', 'ignore', 'ignore'], detached: input === undefined });
      child.on('error', () => resolve(false));
      child.on('close', (code) => resolve(code === 0));
      if (input !== undefined) {
        child.stdin?.end(input);
      } else {
        child.unref();
        // A detached opener that started is good enough; do not wait for the file manager.
        setTimeout(() => resolve(true), 300);
      }
    } catch {
      resolve(false);
    }
  });
}

export async function openPath(p: string): Promise<boolean> {
  if (process.platform === 'darwin') return run('open', [p]);
  if (process.platform === 'win32') return run('explorer', [p]);
  return run('xdg-open', [p]);
}

export async function copyText(text: string): Promise<boolean> {
  const candidates: [string, string[]][] =
    process.platform === 'darwin'
      ? [['pbcopy', []]]
      : process.platform === 'win32'
        ? [['clip', []]]
        : [['wl-copy', []], ['xclip', ['-selection', 'clipboard']], ['xsel', ['--clipboard', '--input']]];
  for (const [cmd, args] of candidates) {
    if (await run(cmd, args, text)) return true;
  }
  return false;
}
