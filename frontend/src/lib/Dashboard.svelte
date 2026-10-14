<script lang="ts">
  import 'gridstack/dist/gridstack.min.css';
  import { GridStack } from 'gridstack';

  import Tape from './Tape.svelte';

  let gridContainer: HTMLElement;

  $effect(() => {
    const grid = GridStack.init({
      margin: 8,
      cellHeight: 60,
      float: true,
    }, gridContainer);

    const savedLayout = localStorage.getItem('trading-workspace-layout');
    if (savedLayout) {
      grid.load(JSON.parse(savedLayout));
    }

    grid.on('change', () => {
      const currentLayout = grid.save();
      localStorage.setItem('trading-workspace-layout', JSON.stringify(currentLayout));
    });

    return () => {
      grid.destroy(false);
    };
  });
</script>

<!-- The main GridStack container -->
<div bind:this={gridContainer} class="grid-stack">
  
  <!-- Module 1: The Tape -->
  <div class="grid-stack-item" gs-id="tape-module" gs-w="3" gs-h="8" gs-x="0" gs-y="0" gs-min-w="2">
    <div class="grid-stack-item-content bg-slate-900 border border-slate-700 rounded-md overflow-hidden flex flex-col">
      <div class="bg-slate-800 px-3 py-1 text-xs text-slate-400 font-bold uppercase tracking-wider cursor-move">
        L1 Tape
      </div>
      <div class="flex-1 overflow-y-auto p-2">
        <Tape />
        <!-- Tape data streaming... -->
      </div>
    </div>
  </div>

  <!-- Module 2: Chart Placeholder -->
  <div class="grid-stack-item" gs-id="chart-module" gs-w="6" gs-h="8" gs-x="3" gs-y="0">
    <div class="grid-stack-item-content bg-slate-900 border border-slate-700 rounded-md">
      <div class="bg-slate-800 px-3 py-1 text-xs text-slate-400 font-bold uppercase tracking-wider cursor-move">
        ES Chart
      </div>
    </div>
  </div>

</div>