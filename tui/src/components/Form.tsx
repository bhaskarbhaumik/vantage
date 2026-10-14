// Keyboard-driven form used by the New dossier and Export screens.
//   up/down (j/k) move  enter edit/toggle/activate  space or left/right cycle  esc cancels an edit
import React, { useState } from 'react';
import { Box } from 'ink';
import TextInput from 'ink-text-input';
import { useKeys } from './context.js';
import { Icon, Row, Txt, useIcon, useUi } from './ui.js';

export type FieldValue = string | boolean | string[];

export type FieldDef =
  | { kind: 'section'; label: string }
  | { kind: 'text'; id: string; label: string; hint?: string; placeholder?: string; required?: boolean }
  | { kind: 'choice'; id: string; label: string; options: string[]; hint?: string; labels?: Record<string, string> }
  | { kind: 'bool'; id: string; label: string; hint?: string }
  | { kind: 'multi'; id: string; label: string; options: string[]; hint?: string }
  | { kind: 'button'; id: string; label: string; hint?: string };

type Focusable = Exclude<FieldDef, { kind: 'section' }>;

export interface FormProps {
  fields: FieldDef[];
  values: Record<string, FieldValue>;
  onChange(id: string, value: FieldValue): void;
  onSubmit(buttonId: string): void;
  errors?: Record<string, string>;
  labelWidth?: number;
  maxRows?: number;
  // When false the form ignores keys (e.g. while a modal is open).
  active?: boolean;
}

function isFocusable(f: FieldDef): f is Focusable {
  return f.kind !== 'section';
}

function cycle(options: string[], cur: string, dir: 1 | -1): string {
  const i = options.indexOf(cur);
  const n = options.length;
  return options[((i < 0 ? 0 : i + dir) % n + n) % n];
}

export const Form: React.FC<FormProps> = ({
  fields,
  values,
  onChange,
  onSubmit,
  errors = {},
  labelWidth = 22,
  maxRows = 40,
  active = true,
}) => {
  const ui = useUi();
  const ic = useIcon();
  const focusables = fields.filter(isFocusable);
  const [cursor, setCursor] = useState(0);
  const [sub, setSub] = useState(0);
  const [editing, setEditing] = useState<{ id: string; original: string } | null>(null);
  const cur = Math.min(cursor, Math.max(0, focusables.length - 1));
  const focused = focusables[cur];

  const move = (d: number) => {
    setCursor((c) => Math.max(0, Math.min(focusables.length - 1, Math.min(c, focusables.length - 1) + d)));
    setSub(0);
  };

  useKeys((input, key) => {
    if (!active) return false;
    if (editing) {
      if (key.escape) {
        onChange(editing.id, editing.original);
        setEditing(null);
      } else if (key.upArrow || key.downArrow || key.tab) {
        // Commit and move, so tab-like navigation never loses typed text.
        setEditing(null);
        move(key.upArrow || (key.tab && key.shift) ? -1 : 1);
      }
      return true;
    }
    if (!focused) return false;
    if (key.upArrow || input === 'k') {
      move(-1);
      return true;
    }
    if (key.downArrow || input === 'j') {
      move(1);
      return true;
    }
    const v = values[focused.id];
    switch (focused.kind) {
      case 'text':
        if (key.return || input === 'e') {
          setEditing({ id: focused.id, original: typeof v === 'string' ? v : '' });
          return true;
        }
        if (key.backspace || key.delete) {
          onChange(focused.id, '');
          return true;
        }
        return false;
      case 'choice': {
        const s = typeof v === 'string' ? v : focused.options[0];
        if (key.return || input === ' ' || key.rightArrow || input === 'l') {
          onChange(focused.id, cycle(focused.options, s, 1));
          return true;
        }
        if (key.leftArrow || input === 'h') {
          onChange(focused.id, cycle(focused.options, s, -1));
          return true;
        }
        return false;
      }
      case 'bool':
        if (key.return || input === ' ' || key.leftArrow || key.rightArrow) {
          onChange(focused.id, !(v === true));
          return true;
        }
        return false;
      case 'multi': {
        const sel = Array.isArray(v) ? v : [];
        if (key.leftArrow || input === 'h') {
          setSub((x) => Math.max(0, x - 1));
          return true;
        }
        if (key.rightArrow || input === 'l') {
          setSub((x) => Math.min(focused.options.length - 1, x + 1));
          return true;
        }
        if (key.return || input === ' ') {
          const opt = focused.options[Math.min(sub, focused.options.length - 1)];
          onChange(focused.id, sel.includes(opt) ? sel.filter((o) => o !== opt) : focused.options.filter((o) => o === opt || sel.includes(o)));
          return true;
        }
        return false;
      }
      case 'button':
        if (key.return || input === ' ') {
          onSubmit(focused.id);
          return true;
        }
        return false;
    }
  });

  // Window the rows around the cursor when the form is taller than the screen.
  const rows = fields.map((f, i) => ({ f, i }));
  const focusedRow = rows.findIndex((r) => r.f === focused);
  const start = Math.max(0, Math.min(focusedRow - Math.floor(maxRows / 2), rows.length - maxRows));
  const visible = rows.length > maxRows ? rows.slice(start, start + maxRows) : rows;
  const valueWidth = Math.max(10, ui.width - labelWidth - 10);

  return (
    <Box flexDirection="column">
      {rows.length > maxRows && start > 0 ? <Txt dim>  ...</Txt> : null}
      {visible.map(({ f, i }) => {
        if (f.kind === 'section') {
          return (
            <Box key={`s${i}`} marginTop={i === 0 ? 0 : 1}>
              <Txt tone="accent2" bold>
                {f.label}
              </Txt>
            </Box>
          );
        }
        const sel = f === focused;
        const v = values[f.id];
        const err = errors[f.id];
        let body: React.ReactNode;
        if (f.kind === 'text') {
          if (editing?.id === f.id) {
            body = (
              <Box>
                <Icon name="edit" tone="accent" />
                <TextInput
                  value={typeof v === 'string' ? v : ''}
                  onChange={(nv) => onChange(f.id, nv)}
                  onSubmit={() => setEditing(null)}
                  focus
                  showCursor
                />
              </Box>
            );
          } else {
            const s = typeof v === 'string' ? v : '';
            body = s ? (
              <Txt wrap="truncate">{s.length > valueWidth ? `${s.slice(0, valueWidth - 3)}...` : s}</Txt>
            ) : (
              <Txt dim>{f.placeholder ?? (f.required ? '(required)' : '-')}</Txt>
            );
          }
        } else if (f.kind === 'choice') {
          const s = typeof v === 'string' ? v : f.options[0];
          const shown = f.labels?.[s] ?? s;
          body = (
            <Box>
              <Txt tone={sel ? 'accent' : undefined} bold={sel}>
                {sel ? `${ui.prefs.icons === 'ascii' ? '<' : '‹'} ${shown} ${ui.prefs.icons === 'ascii' ? '>' : '›'}` : shown}
              </Txt>
              <Txt dim>  {f.options.length > 1 ? `(${f.options.indexOf(s) + 1}/${f.options.length})` : ''}</Txt>
            </Box>
          );
        } else if (f.kind === 'bool') {
          body = (
            <Box>
              <Icon name={v === true ? 'toggleOn' : 'toggleOff'} tone={v === true ? 'ok' : 'muted'} />
              <Txt>{v === true ? 'on' : 'off'}</Txt>
            </Box>
          );
        } else if (f.kind === 'multi') {
          const selected = Array.isArray(v) ? v : [];
          body = (
            <Box>
              {f.options.map((o, oi) => {
                const on = selected.includes(o);
                const hot = sel && oi === Math.min(sub, f.options.length - 1);
                return (
                  <Box key={o} marginRight={2}>
                    <Txt tone={on ? 'ok' : 'muted'}>{ic(on ? 'checkOn' : 'checkOff')} </Txt>
                    <Txt bold={hot} underline={hot} tone={hot ? 'accent' : undefined}>
                      {hot && !ui.prefs.color ? `>${o}<` : o}
                    </Txt>
                  </Box>
                );
              })}
            </Box>
          );
        } else {
          body = (
            <Box>
              <Txt tone={sel ? 'accent' : 'ok'} bold inverse={sel}>
                {` ${ic('rocket')} ${f.label} `}
              </Txt>
            </Box>
          );
        }
        return (
          <Box key={f.id} flexDirection="column">
            <Row selected={sel}>
              {f.kind === 'button' ? (
                body
              ) : (
                <Box>
                  <Box width={labelWidth} flexShrink={0}>
                    <Txt tone={sel ? 'accent' : undefined} bold={sel}>
                      {f.label}
                    </Txt>
                  </Box>
                  {body}
                </Box>
              )}
            </Row>
            {err ? (
              <Box marginLeft={labelWidth + 2}>
                <Icon name="warn" tone="err" />
                <Txt tone="err">{err}</Txt>
              </Box>
            ) : null}
          </Box>
        );
      })}
      {rows.length > maxRows && start + maxRows < rows.length ? <Txt dim>  ...</Txt> : null}
      {focused && 'hint' in focused && focused.hint ? (
        <Box marginTop={1}>
          <Icon name="info" tone="info" />
          <Txt dim wrap="wrap">
            {focused.hint}
          </Txt>
        </Box>
      ) : null}
    </Box>
  );
};
