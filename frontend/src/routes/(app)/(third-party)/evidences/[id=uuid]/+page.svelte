<script lang="ts">
	import { page } from '$app/stores';
	import ConfirmModal from '$lib/components/Modals/ConfirmModal.svelte';
	import ModelTable from '$lib/components/ModelTable/ModelTable.svelte';
	import { URL_MODEL_MAP } from '$lib/utils/crud';
	import { getModelInfo } from '$lib/utils/crud.js';
	import { isURL } from '$lib/utils/helpers';
	import type { ModalComponent, ModalSettings, ModalStore } from '@skeletonlabs/skeleton';
	import { getModalStore, Tab, TabGroup } from '@skeletonlabs/skeleton';
	import { onMount } from 'svelte';
	import type { PageData } from './$types';

	import { safeTranslate } from '$lib/utils/i18n';
	import * as m from '$paraglide/messages';
	import Anchor from '$lib/components/Anchor/Anchor.svelte';

	export let data: PageData;

	interface Attachment {
		type: string;
		url: string;
		fileExists: boolean;
	}

	let attachment: Attachment | undefined = undefined;
	const modalStore: ModalStore = getModalStore();

	function modalConfirm(id: string, name: string, action: string): void {
		const modalComponent: ModalComponent = {
			ref: ConfirmModal,
			props: {
				_form: data.attachmentDeleteForm,
				id: id,
				debug: false,
				URLModel: getModelInfo('evidences').urlModel,
				formAction: action
			}
		};
		const modal: ModalSettings = {
			type: 'component',
			component: modalComponent,
			// Data
			title: m.confirmModalTitle(),
			body: `${m.confirmModalMessage()}: ${name}?`
		};
		modalStore.trigger(modal);
	}

	onMount(async () => {
		const fetchAttachment = async () => {
			const res = await fetch(`./${data.evidence.id}/attachment`);
			const blob = await res.blob();
			return {
				type: blob.type,
				url: URL.createObjectURL(blob),
				fileExists: res.ok
			};
		};
		attachment = data.evidence.attachment ? await fetchAttachment() : undefined;
	});

	const user = $page.data.user;
	const model = URL_MODEL_MAP['evidences'];
	const canEditObject: boolean = Object.hasOwn(user.permissions, `change_${model.name}`);

	let tabSet = 0;
</script>

<div class="flex flex-col space-y-4 whitespace-pre-line">
	<div class="card px-6 py-4 bg-white flex flex-row justify-between shadow-lg">
		<div class="flex flex-col space-y-2 whitespace-pre-line">
			{#each Object.entries(data.evidence).filter( ([key, _]) => ['name', 'description', 'folder', 'attachment', 'link', 'comment'].includes(key) ) as [key, value]}
				<div class="flex flex-col">
					<div
						class="text-sm font-medium text-gray-800 capitalize-first"
						data-testid={key.replace('_', '-') + '-field-title'}
					>
						{safeTranslate(key)}
					</div>
					<ul class="text-sm">
						<li
							class="text-gray-600 list-none"
							data-testid={!Array.isArray(value) || value.length <= 0
								? key.replace('_', '-') + '-field-value'
								: null}
						>
							{#if value}
								{#if Array.isArray(value)}
									<ul>
										{#if value.length > 0}
											{#each value as val}
												<li data-testid={key.replace('_', '-') + '-field-value'}>
													{#if val.str && val.id}
														{@const itemHref = `/${
															URL_MODEL_MAP[data.URLModel]['foreignKeyFields']?.find(
																(item) => item.field === key
															)?.urlModel
														}/${val.id}`}
														<Anchor href={itemHref} class="anchor">{val.str}</Anchor>
													{:else}
														{value}
													{/if}
												</li>
											{/each}
										{:else}
											--
										{/if}
									</ul>
								{:else if value.id}
									{@const itemHref = `/${
										URL_MODEL_MAP['evidences']['foreignKeyFields']?.find(
											(item) => item.field === key
										)?.urlModel
									}/${value.id}`}
									<Anchor href={itemHref} class="anchor">{value.str}</Anchor>
								{:else if isURL(value)}
									<Anchor href={value} target="_blank" class="anchor">{value}</Anchor>
								{:else}
									{value.str ?? value}
								{/if}
							{:else}
								--
							{/if}
						</li>
					</ul>
				</div>
			{/each}
		</div>
		<span>
			{#if canEditObject}
				<Anchor
					href={`${$page.url.pathname}/edit?next=${$page.url.pathname}`}
					class="btn variant-filled-primary h-fit"
					data-testid="edit-button"><i class="fa-solid fa-pen-to-square mr-2" /> {m.edit()}</Anchor
				>
			{/if}
		</span>
	</div>
	<div class="card px-6 py-4 bg-white flex flex-col shadow-lg space-y-4">
		<TabGroup>
			<Tab bind:group={tabSet} name="compliance_assessments_tab" value={0}
				>{m.appliedControls()}</Tab
			>
			<Tab bind:group={tabSet} name="risk_assessments_tab" value={1}
				>{m.requirementAssessments()}</Tab
			>
			<svelte:fragment slot="panel">
				{#if tabSet === 0}
					<ModelTable source={data.tables['applied-controls']} URLModel="applied-controls" />
				{/if}
				{#if tabSet === 1}
					<ModelTable
						source={data.tables['requirement-assessments']}
						URLModel="requirement-assessments"
					/>
				{/if}
			</svelte:fragment>
		</TabGroup>
	</div>
	{#if data.evidence.attachment}
		<div class="card px-6 py-4 bg-white flex flex-col shadow-lg space-y-4">
			<div class="flex flex-row justify-between">
				<h4 class="h4 font-semibold" data-testid="attachment-name-title">
					{data.evidence.attachment}
				</h4>
				<div class="space-x-2">
					<Anchor
						href={`./${data.evidence.id}/attachment`}
						class="btn variant-filled-primary h-fit"
						data-testid="attachment-download-button"
						><i class="fa-solid fa-download mr-2" /> {m.download()}</Anchor
					>
					<button
						on:click={(_) => {
							modalConfirm(data.evidence.id, data.evidence.attachment, '?/deleteAttachment');
						}}
						on:keydown={(_) =>
							modalConfirm(data.evidence.id, data.evidence.attachment, '?/deleteAttachment')}
						class="btn variant-filled-tertiary h-full"><i class="fa-solid fa-trash" /></button
					>
				</div>
			</div>
			{#if attachment}
				{#if attachment.type.startsWith('image')}
					<img src={attachment.url} alt="attachment" />
				{:else if attachment.type === 'application/pdf'}
					<embed src={attachment.url} type="application/pdf" width="100%" height="600px" />
				{:else}
					<div class="flex items-center justify-center space-x-4">
						{#if !attachment.fileExists}
							<p class="text-error-500 font-bold">{m.couldNotFindAttachmentMessage()}</p>
						{:else}
							<p class="font-bold text-sm">{m.NoPreviewMessage()}</p>
						{/if}
					</div>
				{/if}
			{:else}
				<span data-testid="loading-field">
					{m.loading()}...
				</span>
			{/if}
		</div>
	{/if}
</div>
