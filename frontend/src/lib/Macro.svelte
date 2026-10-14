<script lang="ts">
  import MacroEvent from "./types/MacroEvent.svelte";

  let events = $state<MacroEvent[]>([]);
  let error = $state<string | null>(null);
  let now = $state(new Date().getTime());

  $effect(() => {
    const timer = setInterval(() => {
      now = new Date().getTime();
    }, 1000);
    return () => clearInterval(timer);
  });

  $effect(() => {
    const fetchMacro = async () => {
      try {
        const res = await fetch("http://localhost:8000/macro");
        if (!res.ok) throw new Error("Macro feed offline");
        const data = await res.json();


        const threshold = now - 4 * 60 * 60 * 1000;
        events = data.filter(
          (e: MacroEvent) => new Date(e.date).getTime() > threshold,
        );
      } catch (e) {
        error = "Calendar unavailable";
      }
    };

    fetchMacro();
    // Refresh the actual schedule every 5 minutes
    const poll = setInterval(fetchMacro, 300000);
    return () => clearInterval(poll);
  });

  function getCountdown(eventDateStr: string, currentTime: number) {
    const eventTime = new Date(eventDateStr).getTime();
    const diff = eventTime - currentTime;

    if (diff < 0 && diff > -300000) return "RELEASED"; // 5 min post-release window
    if (diff < 0) return "DONE";

    const h = Math.floor(diff / (1000 * 60 * 60));
    const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const s = Math.floor((diff % (1000 * 60)) / 1000);

    return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  }
</script>

<div
  class="flex flex-col h-full bg-slate-950 border border-slate-800 rounded-md overflow-hidden font-sans text-sm"
>
  <!-- Header Bar -->
  <div
    class="flex items-center justify-between bg-slate-900/90 px-3 py-2 border-b border-slate-800 shrink-0"
  >
    <span class="text-xs font-bold uppercase tracking-wider text-slate-300"
      >Macro Calendar</span
    >
    <span
      class="text-[10px] font-mono font-medium px-1.5 py-0.5 rounded bg-slate-800 text-slate-400"
    >
      USD IMPACT
    </span>
  </div>

  <div class="flex-1 overflow-y-auto overflow-x-hidden p-2">
    {#if error}
      <div
        class="flex h-16 items-center justify-center text-rose-400 text-xs font-bold uppercase"
      >
        {error}
      </div>
    {:else if events.length === 0}
      <div
        class="flex h-16 items-center justify-center text-slate-500 text-xs font-mono"
      >
        No High/Med USD events left today
      </div>
    {:else}
      <table class="w-full text-left border-collapse">
        <thead>
          <tr
            class="border-b border-slate-800 text-[10px] font-mono text-slate-500 uppercase"
          >
            <th class="py-2 pl-2 font-medium">Event</th>
            <th class="py-2 font-medium text-center">Impact</th>
            <th class="py-2 font-medium text-right pr-2">Est / Prev</th>
            <th class="py-2 font-medium text-right pr-2">T-Minus</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/50">
          {#each events as event}
            {@const countdown = getCountdown(event.date, now)}
            {@const isHigh = event.impact === "High"}
            {@const isImminent =
              countdown !== "DONE" &&
              countdown !== "RELEASED" &&
              countdown.startsWith("00:0")}

            <tr
              class="hover:bg-slate-900/50 transition-colors {isImminent
                ? 'bg-rose-950/20'
                : ''}"
            >
              <!-- Event Title & Date -->
              <td class="py-2.5 pl-2 max-w-[140px]">
                <div
                  class="text-[11px] font-bold text-slate-200 truncate group-hover:text-white"
                  title={event.title}
                >
                  {event.title}
                </div>
                <div class="text-[9px] font-mono text-slate-500 mt-0.5">
                  {new Date(event.date).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </td>

              <!-- Impact Badge -->
              <td class="py-2.5 text-center">
                <span
                  class="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border {isHigh
                    ? 'bg-rose-950/80 text-rose-400 border-rose-800'
                    : 'bg-amber-950/80 text-amber-400 border-amber-800'}"
                >
                  {event.impact}
                </span>
              </td>

              <!-- Forecast / Previous -->
              <td class="py-2.5 text-right pr-2">
                <div class="text-[10px] font-mono text-slate-300">
                  {event.forecast || "-"}
                </div>
                <div class="text-[9px] font-mono text-slate-600 mt-0.5">
                  {event.previous || "-"}
                </div>
              </td>

              <!-- Countdown Timer -->
              <td class="py-2.5 text-right pr-2 font-mono">
                {#if countdown === "RELEASED"}
                  <span
                    class="text-[11px] font-bold text-emerald-400 animate-pulse"
                    >RELEASED</span
                  >
                {:else if countdown === "DONE"}
                  <span class="text-[11px] text-slate-600 line-through"
                    >DONE</span
                  >
                {:else}
                  <span
                    class="text-[11px] font-bold {isImminent
                      ? 'text-rose-400 animate-pulse'
                      : 'text-slate-300'}"
                  >
                    {countdown}
                  </span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>
</div>
