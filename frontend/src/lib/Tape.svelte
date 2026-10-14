<script lang="ts">
  import { onMount } from "svelte";

  interface TradePrint {
    timestamp: number;
    symbol: string;
    price: number;
    size: number;
    side: "buy" | "sell" | "neutral";
  }

  let trades = $state<TradePrint[]>([]);
  let ws: WebSocket;

  function getTradeColor(side: string, size: number) {
    if (side === "neutral") return "text-slate-400";

    if (side === "buy") {
      if (size >= 10) return "bg-emerald-500 text-white font-bold";

      if (size >= 5) return "bg-emerald-700 text-emerald-50";
      return "bg-emerald-950/50 text-emerald-400";
    }

    if (side === "sell") {
      if (size >= 10) return "bg-rose-600 text-white font-bold";

      if (size >= 5) return "bg-rose-800 text-rose-50";

      return "bg-rose-950/50 text-rose-400";
    }

    return "";
  }
  onMount(() => {
    ws = new WebSocket("ws://localhost:8000/ws/tape");

    ws.onopen = () => console.log("Connected to FastAPI tape stream");

    ws.onmessage = (event) => {
      try {
        const trade: TradePrint = JSON.parse(event.data);

        // Reassigning the array triggers Svelte's reactivity
        trades = [trade, ...trades];

        // Prevent DOM freezing by capping the array
        if (trades.length > 100) {
          trades = trades.slice(0, 100);
        }
      } catch (error) {
        console.error("Failed to parse trade:", error);
      }
    };

    // The function returned by onMount acts as the cleanup/teardown hook
    return () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
        console.log("WebSocket connection closed cleanly");
      }
    };
  });
</script>

<div
  class="bg-slate-950 text-slate-200 font-mono h-full flex flex-col w-full"
>
  <div
    class="bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden flex flex-col"
  >
    <div
      class="flex justify-between items-center p-3 bg-slate-800/50 border-b border-slate-700 font-bold text-sm"
    >
      <span class="w-24 text-left">TIME</span>
      <span class="w-24">PRICE</span>
      <span class="w-16 text-right">SIZE</span>
    </div>

    <!-- Tape Feed -->
    <div class="overflow-y-auto h-150">
      {#each trades as trade}
        <div
          class="flex justify-between items-center p-2 text-sm border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors {getTradeColor(
            trade.side,
            trade.size,
          )}"
        >
          <span class="w-24 text-right text-xs">
            {new Date(trade.timestamp * 1000).toLocaleString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
              fractionalSecondDigits: 3,
              hour12: false,
            })}
          </span>
          <span class="w-24 font-medium">{trade.price.toFixed(2)}</span>

          <span
            class="w-16 text-right font-bold px-2 py-0.5 rounded
            {trade.side === 'buy' ? 'bg-emerald-900/20' : ''}
            {trade.side === 'sell' ? 'bg-rose-900/20' : ''}"
          >
            {trade.size}
          </span>
        </div>
      {/each}
    </div>
  </div>
</div>
