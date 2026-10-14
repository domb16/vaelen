<script lang="ts">
  let internals = $state({ add: 0, tick: 0 });
  let error = $state<string | null>(null);

  $effect(() => {
    const fetchInternals = async () => {
      try {
        const res = await fetch('http://localhost:8000/internals');
        if (!res.ok) throw new Error('Internals feed offline');
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        
        internals = data;
        error = null;
      } catch (e) {
        error = 'Internals disconnected';
      }
    };

    fetchInternals();
    const interval = setInterval(fetchInternals, 15000);
    return () => clearInterval(interval);
  });

  // Calculate percentage for CSS bar (0 to 100%, center is 50%)
  function getAddPercentage(val: number) {
    // $ADD rarely exceeds +/- 2500 
    const min = -2500;
    const max = 2500;
    let pct = ((val - min) / (max - min)) * 100;
    return Math.max(0, Math.min(100, pct));
  }

  function getTickPercentage(val: number) {
    // $TICK structural extremes are +/- 1200 to 1500
    const min = -1500;
    const max = 1500;
    let pct = ((val - min) / (max - min)) * 100;
    return Math.max(0, Math.min(100, pct));
  }
</script>

<div class="flex flex-col h-full bg-slate-950 border border-slate-800 rounded-md overflow-hidden font-sans text-sm">
  <div class="flex items-center justify-between bg-slate-900/90 px-3 py-2 border-b border-slate-800 shrink-0">
    <span class="text-xs font-bold uppercase tracking-wider text-slate-300">Market Internals</span>
    <span class="text-[10px] font-mono text-slate-500">15s POLL</span>
  </div>

  <div class="flex flex-col flex-1 p-4 justify-center gap-8">
    {#if error}
      <div class="text-rose-400 text-xs font-bold uppercase text-center">{error}</div>
    {:else}
      <!-- $ADD Gauge -->
      <div class="space-y-2">
        <div class="flex justify-between items-end">
          <span class="text-[11px] font-bold text-slate-400 uppercase">$ADD (Adv/Dec)</span>
          <span class="font-mono font-bold text-lg {internals.add > 0 ? 'text-emerald-400' : 'text-rose-400'}">
            {internals.add > 0 ? '+' : ''}{internals.add.toFixed(0)}
          </span>
        </div>
        <div class="relative w-full h-3.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800 shadow-inner">
          <div class="absolute top-0 bottom-0 left-1/2 w-px bg-slate-600 z-10"></div>
          {#if internals.add > 0}
            <div 
              class="absolute top-0 bottom-0 left-1/2 bg-emerald-500/90 transition-all duration-500" 
              style="width: {getAddPercentage(internals.add) - 50}%"
            ></div>
          {:else}
            <div 
              class="absolute top-0 bottom-0 bg-rose-500/90 transition-all duration-500" 
              style="left: {getAddPercentage(internals.add)}%; right: 50%"
            ></div>
          {/if}
        </div>
        <div class="flex justify-between text-[9px] font-mono text-slate-600">
          <span>-2500</span>
          <span>0</span>
          <span>+2500</span>
        </div>
      </div>

      <!-- $TICK Gauge -->
      <div class="space-y-2">
        <div class="flex justify-between items-end">
          <span class="text-[11px] font-bold text-slate-400 uppercase">$TICK (NYSE)</span>
          <span class="font-mono font-bold text-lg {internals.tick > 0 ? 'text-emerald-400' : 'text-rose-400'}">
            {internals.tick > 0 ? '+' : ''}{internals.tick.toFixed(0)}
          </span>
        </div>
        <div class="relative w-full h-3.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800 shadow-inner">
          <div class="absolute top-0 bottom-0 left-1/2 w-px bg-slate-600 z-10"></div>
          {#if internals.tick > 0}
            <div 
              class="absolute top-0 bottom-0 left-1/2 bg-emerald-500/90 transition-all duration-500" 
              style="width: {getTickPercentage(internals.tick) - 50}%"
            ></div>
          {:else}
            <div 
              class="absolute top-0 bottom-0 bg-rose-500/90 transition-all duration-500" 
              style="left: {getTickPercentage(internals.tick)}%; right: 50%"
            ></div>
          {/if}
        </div>
        <div class="flex justify-between text-[9px] font-mono text-slate-600">
          <span>-1500 (OVERSOLD)</span>
          <span>0</span>
          <span>+1500 (OVERBOUGHT)</span>
        </div>
      </div>
    {/if}
  </div>
</div>