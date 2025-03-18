<script lang="ts">
	export let timestamp: string;
	export let type: string;
	export let username: string;
	export let message: string;
</script>

<div class="log-item">
	<span class="text-gray-400"
		>{timestamp}
		{#if type === "INF"}
			<span class="text-green-500">INF</span>
		{:else if type === "ERR"}
			<span class="text-red-500">ERR</span>
		{/if}
		<span class="text-sky-500">{username}</span>
		<span class="text-black dark:text-white"> {@html message}</span>
	</span>
</div>

<style>
	.log-item {
		line-height: 1.5;
		margin-bottom: 2px;
	}
</style>
