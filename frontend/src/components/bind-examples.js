import { EXAMPLES } from '../utils/examples.js';

export function bindExampleSelector({
  selectEl,
  inputEl,
  examples = EXAMPLES,
  defaultKey = 'default',
}) {
  const applySelection = () => {
    inputEl.value = examples[selectEl.value] || examples[defaultKey] || '';
  };

  selectEl.value = defaultKey;
  applySelection();
  selectEl.addEventListener('change', applySelection);
}
