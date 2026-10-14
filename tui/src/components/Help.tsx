// Help overlay (`?`): global keybindings plus the current screen's own keys.
import React from 'react';
import { Box } from 'ink';
import { Panel, Txt, useUi } from './ui.js';
import { pad } from '../lib/format.js';

export const GLOBAL_KEYS: [string, string][] = [
  ['tab / shift-tab', 'next / previous screen'],
  ['1-8', 'jump: home new live runs export doctor backends config'],
  ['esc', 'back (or cancel an edit)'],
  ['?', 'toggle this help'],
  ['q', 'quit (asks first while a run or export is active)'],
  ['ctrl-c', 'quit now (stops the engine)'],
];

export const Help: React.FC<{ screenTitle: string; screenKeys: [string, string][] }> = ({ screenTitle, screenKeys }) => {
  const ui = useUi();
  const keyW = ui.narrow ? 16 : 20;
  const section = (title: string, keys: [string, string][]) => (
    <Box flexDirection="column" marginBottom={1}>
      <Txt tone="accent2" bold>
        {title}
      </Txt>
      {keys.map(([k, d]) => (
        <Box key={k}>
          <Txt tone="accent" bold>
            {pad(k, keyW)}
          </Txt>
          <Txt wrap="truncate">{d}</Txt>
        </Box>
      ))}
    </Box>
  );
  return (
    <Panel title="Keybindings" icon="keyboard" focused right={<Txt dim>esc or ? to close</Txt>}>
      {section('Global', GLOBAL_KEYS)}
      {screenKeys.length ? section(screenTitle, screenKeys) : null}
      <Txt dim>Mouse is not needed; every action has a key.</Txt>
    </Panel>
  );
};
