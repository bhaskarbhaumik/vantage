// Presentation primitives. Every glyph and colour in the TUI goes through these so that --ascii,
// --no-color, --theme and --no-animations hold everywhere.
import React, { createContext, useContext, useEffect, useState } from 'react';
import { Box, Text, useStdout } from 'ink';
import Spinner from 'ink-spinner';
import { barChars, borderStyle, icon as iconFor, type IconName, spinnerType, toAscii } from '../lib/icons.js';
import { DEFAULT_PREFS, PALETTES, type Palette, type Tone, type UiPrefs } from '../lib/theme.js';

export interface UiState {
  prefs: UiPrefs;
  palette: Palette;
  width: number;
  height: number;
  narrow: boolean;
}

export const NARROW_BELOW = 100;

const UiContext = createContext<UiState>({
  prefs: DEFAULT_PREFS,
  palette: PALETTES.dark,
  width: 100,
  height: 30,
  narrow: false,
});

export function useUi(): UiState {
  return useContext(UiContext);
}

export function useTerminalSize(override?: { width?: number; height?: number }): { width: number; height: number } {
  const { stdout } = useStdout();
  const read = () => ({
    width: override?.width ?? (stdout?.columns || 80),
    height: override?.height ?? (stdout?.rows || 30),
  });
  const [size, setSize] = useState(read);
  useEffect(() => {
    if (!stdout || override?.width) return;
    const onResize = () => setSize(read());
    stdout.on('resize', onResize);
    return () => {
      stdout.off('resize', onResize);
    };
  }, [stdout]); // eslint-disable-line react-hooks/exhaustive-deps
  return size;
}

export const UiProvider: React.FC<{
  prefs: UiPrefs;
  width?: number;
  height?: number;
  children: React.ReactNode;
}> = ({ prefs, width, height, children }) => {
  const size = useTerminalSize({ width, height });
  const value: UiState = {
    prefs,
    palette: PALETTES[prefs.theme],
    width: size.width,
    height: size.height,
    narrow: size.width < NARROW_BELOW,
  };
  return <UiContext.Provider value={value}>{children}</UiContext.Provider>;
};

function asciiChildren(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, (c) => (typeof c === 'string' ? toAscii(c) : c));
}

export interface TxtProps {
  tone?: Tone;
  bold?: boolean;
  dim?: boolean;
  underline?: boolean;
  inverse?: boolean;
  wrap?: 'wrap' | 'truncate' | 'truncate-end' | 'truncate-middle' | 'truncate-start';
  children?: React.ReactNode;
}

// Ink <Text> that drops every style in --no-color mode and folds strings to ASCII in --ascii mode.
export const Txt: React.FC<TxtProps> = ({ tone, bold, dim, underline, inverse, wrap, children }) => {
  const ui = useUi();
  const ascii = ui.prefs.icons === 'ascii';
  const kids = ascii ? asciiChildren(children) : children;
  const inner = !ui.prefs.color ? (
    <Text wrap={wrap}>{kids}</Text>
  ) : (
    <Text
      color={tone ? ui.palette[tone] : undefined}
      bold={bold}
      dimColor={dim}
      underline={underline}
      inverse={inverse}
      wrap={wrap}
    >
      {kids}
    </Text>
  );
  if (!ascii || children === undefined || children === null) return inner;
  // Ink truncates with a Unicode ellipsis after layout; fold it back to ASCII on the final line.
  return React.createElement(
    'ink-text',
    { style: { flexGrow: 0, flexShrink: 1, flexDirection: 'row', textWrap: wrap ?? 'wrap' }, internal_transform: asciiLine },
    inner,
  );
};

function asciiLine(line: string): string {
  return line.replace(/\u2026/g, '.');
}

// One table row rendered as a single line of inline text: never wraps, truncates at the edge.
export const Line: React.FC<{ selected?: boolean; pointer?: boolean; children: React.ReactNode }> = ({
  selected = false,
  pointer = true,
  children,
}) => {
  const ui = useUi();
  const p = iconFor('pointer', ui.prefs.icons);
  return (
    <Txt wrap="truncate">
      {pointer ? (
        <Txt tone="accent" bold>
          {selected ? p : ' '.repeat(p.length)}{' '}
        </Txt>
      ) : null}
      {children}
    </Txt>
  );
};

export function useIcon(): (name: IconName) => string {
  const ui = useUi();
  return (name) => iconFor(name, ui.prefs.icons);
}

export const Icon: React.FC<{ name: IconName; tone?: Tone; bold?: boolean; space?: boolean }> = ({
  name,
  tone,
  bold,
  space = true,
}) => {
  const ui = useUi();
  const g = iconFor(name, ui.prefs.icons);
  if (!g) return null;
  return (
    <Txt tone={tone} bold={bold}>
      {g}
      {space ? ' ' : ''}
    </Txt>
  );
};

export const Spin: React.FC<{ tone?: Tone }> = ({ tone = 'info' }) => {
  const ui = useUi();
  if (!ui.prefs.animations) return <Txt tone={tone}>{iconFor('running', ui.prefs.icons)}</Txt>;
  return (
    <Txt tone={tone}>
      <Spinner type={spinnerType(ui.prefs.icons)} />
    </Txt>
  );
};

export function barString(fraction: number, width: number, mode: UiPrefs['icons']): string {
  const c = barChars(mode);
  const inner = Math.max(1, width - c.open.length - c.close.length);
  const f = Math.max(0, Math.min(1, Number.isFinite(fraction) ? fraction : 0));
  const full = Math.round(f * inner);
  return `${c.open}${c.full.repeat(full)}${c.empty.repeat(inner - full)}${c.close}`;
}

export const Bar: React.FC<{ fraction: number; width: number; tone?: Tone }> = ({ fraction, width, tone = 'accent' }) => {
  const ui = useUi();
  return (
    <Txt tone={tone}>
      {barString(fraction, width, ui.prefs.icons)}
    </Txt>
  );
};

export const Panel: React.FC<{
  title?: string;
  icon?: IconName;
  tone?: Tone;
  focused?: boolean;
  width?: number | string;
  height?: number;
  flexGrow?: number;
  flexShrink?: number;
  minWidth?: number;
  right?: React.ReactNode;
  children?: React.ReactNode;
}> = ({ title, icon, tone, focused, width, height, flexGrow, flexShrink, minWidth, right, children }) => {
  const ui = useUi();
  const borderColor = ui.prefs.color ? ui.palette[focused ? 'accent' : tone ?? 'muted'] : undefined;
  return (
    <Box
      flexDirection="column"
      borderStyle={borderStyle(ui.prefs.icons)}
      borderColor={borderColor}
      paddingX={1}
      width={width}
      height={height}
      flexGrow={flexGrow}
      flexShrink={flexShrink}
      minWidth={minWidth}
    >
      {title ? (
        <Box justifyContent="space-between">
          <Box>
            {icon ? <Icon name={icon} tone={tone ?? 'accent'} /> : null}
            <Txt bold tone={tone ?? (focused ? 'accent' : undefined)}>
              {title}
            </Txt>
          </Box>
          {right ? <Box>{right}</Box> : null}
        </Box>
      ) : null}
      {children}
    </Box>
  );
};

export const Badge: React.FC<{ tone: Tone; icon?: IconName; children: React.ReactNode }> = ({ tone, icon, children }) => {
  const ui = useUi();
  const [l, r] = ui.prefs.icons === 'ascii' ? ['[', ']'] : ['', ''];
  return (
    <Txt tone={tone} bold>
      {l}
      {icon ? `${iconFor(icon, ui.prefs.icons)} ` : ''}
      {children}
      {r}
    </Txt>
  );
};

export const AuthBadge: React.FC<{ mode: string }> = ({ mode }) =>
  mode === 'api-key' ? (
    <Badge tone="warn" icon="billing">
      api-key - billed per token
    </Badge>
  ) : (
    <Badge tone="ok" icon="subscription">
      subscription
    </Badge>
  );

export const KeyHints: React.FC<{ hints: [string, string][] }> = ({ hints }) => {
  const ui = useUi();
  const sep = iconFor('dot', ui.prefs.icons);
  return (
    <Box flexWrap="wrap">
      {hints.map(([k, label], i) => (
        <Box key={`${k}-${i}`} marginRight={1}>
          <Txt tone="accent" bold>
            {k}
          </Txt>
          <Txt dim> {label}</Txt>
          {i < hints.length - 1 ? <Txt dim> {sep}</Txt> : null}
        </Box>
      ))}
    </Box>
  );
};

export const ErrorPanel: React.FC<{ title?: string; message: string; hint?: string }> = ({
  title = 'Engine error',
  message,
  hint = 'r retry  esc back',
}) => (
  <Panel title={title} icon="error" tone="err">
    {message.split('\n').slice(0, 12).map((l, i) => (
      <Txt key={i} wrap="wrap">
        {l}
      </Txt>
    ))}
    {hint ? <Txt dim>{hint}</Txt> : null}
  </Panel>
);

export const Loading: React.FC<{ label: string }> = ({ label }) => (
  <Box>
    <Spin />
    <Txt> {label}</Txt>
  </Box>
);

// A row in a list: pointer when selected, accent and bold in colour mode.
export const Row: React.FC<{ selected: boolean; children: React.ReactNode }> = ({ selected, children }) => {
  const ui = useUi();
  const p = iconFor('pointer', ui.prefs.icons);
  const blank = ' '.repeat(p.length);
  return (
    <Box>
      <Txt tone="accent" bold>
        {selected ? p : blank}{' '}
      </Txt>
      {children}
    </Box>
  );
};

export const Field: React.FC<{ label: string; width?: number; children: React.ReactNode }> = ({ label, width = 13, children }) => (
  <Box>
    <Box width={width} flexShrink={0}>
      <Txt dim>{label}</Txt>
    </Box>
    <Box flexGrow={1}>{children}</Box>
  </Box>
);
