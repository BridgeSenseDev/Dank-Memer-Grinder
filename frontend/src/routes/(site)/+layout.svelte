<script lang="ts">
	import "../../app.css";
	import Nav from "$lib/components/Nav.svelte";
	import Header from "$lib/components/Header.svelte";

	interface Props {
		children?: import("svelte").Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="grainy flex min-h-screen flex-col antialiased">
	<Header />
	<div class="grow">
		<div class="flex flex-row">
			<div class="sticky">
				<Nav />
			</div>
			<div class="min-h-navbar relative left-48 mr-48 flex h-full w-full">
				<div class="transition-container flex-1 p-4">
					{@render children?.()}
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.transition-container {
		display: grid;
		grid-template-rows: 1fr;
		grid-template-columns: 1fr;
	}

	.transition-container > :global(*) {
		grid-row: 1;
		grid-column: 1;
	}
</style>
