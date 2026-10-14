<script lang="ts">
  import NewsItem from "./types/NewsItem.svelte";

  let news = $state<NewsItem[]>([]);
  let error = $state<string | null>(null);

  $effect(() => {
    const fetchNews = async () => {
      try {
        const res = await fetch("http://localhost:8000/news");
        if (!res.ok) throw new Error("Failed to connect to backend feed");
        news = await res.json();
        error = null;
      } catch (e) {
        error = "News feed offline";
        console.error(e);
      }
    };

    fetchNews();
    const interval = setInterval(fetchNews, 15000);

    return () => clearInterval(interval);
  });

  function formatTime(unixTime: number) {
    if (!unixTime) return "";
    return new Date(unixTime * 1000).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  }
</script>

<div
  class="flex flex-col h-full bg-slate-950 border border-slate-800 rounded-md overflow-hidden font-sans text-sm"
>
  <div
    class="flex items-center justify-between bg-slate-900/90 px-3 py-2 border-b border-slate-800 shrink-0"
  >
    <div class="flex items-center gap-2">
      <span class="text-sm font-bold uppercase tracking-wider text-slate-300"
        >Market News</span
      >
    </div>

    <div class="flex items-center gap-2">
      <span class="text-[11px] font-mono text-slate-500">15s POLL</span>
      <span class="flex h-2 w-2 relative">
        <span
          class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
        ></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"
        ></span>
      </span>
    </div>
  </div>

  <!-- News List Container -->
  <div
    class="flex-1 overflow-y-auto overflow-x-hidden divide-y divide-slate-800/60 p-2"
  >
    {#if error}
      <div
        class="flex flex-col items-center justify-center h-32 text-rose-400 text-xs gap-1"
      >
        <span class="font-bold uppercase tracking-wider">{error}</span>
        <span class="text-slate-500"
          >Check FastAPI backend on localhost:8000</span
        >
      </div>
    {:else if news.length === 0}
      <div
        class="flex items-center justify-center h-32 text-slate-500 text-xs font-mono"
      >
        Awaiting live news feed...
      </div>
    {:else}
      {#each news as item (item.id)}
        <article
          class="p-2.5 hover:bg-slate-900/50 transition-colors rounded group"
        >
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            class="flex gap-3"
          >
           
            <div class="flex-1 min-w-0 flex flex-col justify-between">
              <div>
             
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                  <span
                    class="text-[11px] font-mono font-semibold text-slate-400"
                  >
                    {formatTime(item.datetime)}
                  </span>

                  <span
                    class="text-[11px] font-bold text-indigo-400 uppercase tracking-wide"
                  >
                    {item.source}
                  </span>

                  {#if item.category}
                    <span
                      class="text-[9px] font-bold px-1.5 py-0.2 uppercase tracking-wider rounded {item.category == "top news" ? "bg-orange-950/80 text-orange-300 border border-orange-800/50": "bg-indigo-950/80 text-indigo-300 border border-indigo-800/50"}"
                    >
                      {item.category}
                    </span>
                  {/if}

                  {#if item.related}
                    <span
                      class="text-[9px] font-mono font-bold px-1.5 py-0.2 uppercase rounded bg-slate-800 text-amber-400 border border-amber-500/30"
                    >
                      ${item.related}
                    </span>
                  {/if}
                </div>

                <!-- Headline -->
                <h3
                  class="text-slate-100 font-semibold text-xs leading-snug group-hover:text-indigo-300 transition-colors line-clamp-2"
                >
                  {item.headline}
                </h3>

                <!-- Summary / Excerpt -->
                {#if item.summary}
                  <p
                    class="text-slate-400 text-[11px] leading-relaxed mt-1 line-clamp-2"
                  >
                    {item.summary}
                  </p>
                {/if}
              </div>
            </div>
          </a>
        </article>
      {/each}
    {/if}
  </div>
</div>
