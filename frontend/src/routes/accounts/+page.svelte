<script lang="ts">
	import DataTable from './data-table.svelte';
	import { fade } from 'svelte/transition';
</script>

<div
	in:fade={{ delay: 100, duration: 250 }}
	out:fade={{ duration: 100 }}
	class="flex h-full w-full flex-col"
>
	<DataTable />
</div>
