<script>
  import Tape from "./lib/Tape.svelte";
  import News from "./lib/News.svelte";
  import Macro from "./lib/Macro.svelte";
  import Internals from "./lib/Internals.svelte";
</script>

<div class="bg-slate-950">
  <div>
    <h2>ES DASHBOARD</h2>
  </div>
  <main class="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 h-screen w-full">
    <div class="h-full min-h-0">
      <Tape />
    </div>

    <div class="flex flex-col gap-6 h-full min-h-0">
      <div class="h-10 lg:h-125">
        <Macro />
      </div>
      <div class="h-75 shrink-0">
        <Internals />
      </div>
      <div class="h-[50vh] lg:h-125">
        <News />
      </div>
    </div>
  </main>
</div>
