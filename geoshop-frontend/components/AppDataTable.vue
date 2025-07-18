<!-- AppDataTable.vue -->
<template>
  <v-container fluid class="pa-0">
    <!-- Pesquisa -->
    <v-text-field
      v-if="searchable"
      v-model="localSearch"
      label="Pesquisar"
      prepend-inner-icon="mdi-magnify"
      clearable
      class="mb-4"
      hide-details
      @input="updateSearch"
    ></v-text-field>

    <!-- Indicador de carregamento -->
    <v-progress-linear
      v-if="loading"
      indeterminate
      color="primary"
      class="mb-4"
    ></v-progress-linear>

    <!-- Mensagem para lista vazia -->
    <v-alert
      v-if="!loading && items.length === 0 && !hideEmptyMessage"
      type="info"
      class="mb-4"
    >
      Nenhum item encontrado.
    </v-alert>

    <!-- Tabela -->
    <v-data-table
      :headers="filteredHeaders"
      :items="items"
      :loading="loading"
      :search="localSearch"
      :items-per-page="itemsPerPage"
      :custom-filter="customFilter"
      :show-select="showSelect"
      v-model="selectedItems"
      :class="tableClass"
      :items-per-page-options="[5, 10, 25, -1]"
      show-footer
      @update:page="updateVisibleItemsCount($event, itemsPerPage)"
      @update:items-per-page="handleItemsPerPageUpdate"
    >
      <!-- Slots dinâmicos para colunas personalizadas -->
      <template v-for="header in headers" :key="header.key" #[`item.${header.key}`]="{ item }">
        <slot :name="`item.${header.key}`" :item="item">
          {{ item[header.key] }}
        </slot>
      </template>

      <!-- Slot para ações -->
      <template v-slot:item.actions="{ item }">
        <slot name="actions" :item="item"></slot>
      </template>
    </v-data-table>

    <!-- Contagem de itens visíveis -->
    <v-chip v-if="showItemCount && items.length > 0" color="primary" class="mt-4">
      Itens: {{ visibleItemsCount }}
    </v-chip>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  headers: {
    type: Array,
    required: true,
    default: () => [],
  },
  items: {
    type: Array,
    required: true,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  showSelect: {
    type: Boolean,
    default: false,
  },
  showItemCount: {
    type: Boolean,
    default: false,
  },
  itemsPerPage: {
    type: Number,
    default: 10,
  },
  customFilter: {
    type: Function,
    default: null,
  },
  tableClass: {
    type: String,
    default: 'elevation-1',
  },
  hideEmptyMessage: {
    type: Boolean,
    default: false,
  },
  hideActions: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:search', 'update:selected', 'update:items-per-page']);

const localSearch = ref('');
const selectedItems = ref([]);
const visibleItemsCount = ref(0);

const filteredHeaders = computed(() => {
  return props.hideActions
    ? props.headers.filter((h) => h.key !== 'actions')
    : props.headers;
});

const updateVisibleItemsCount = (page, itemsPerPage) => {
  if (itemsPerPage === -1) {
    visibleItemsCount.value = props.items.length;
  } else {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    visibleItemsCount.value = Math.min(end, props.items.length) - start;
  }
};

const handleItemsPerPageUpdate = (newItemsPerPage) => {
  emit('update:items-per-page', newItemsPerPage);
  updateVisibleItemsCount(1, newItemsPerPage);
};

watch(localSearch, (newVal) => {
  emit('update:search', newVal);
});

watch(selectedItems, (newVal) => {
  emit('update:selected', newVal);
});

watch(
  () => props.items,
  () => {
    updateVisibleItemsCount(1, props.itemsPerPage);
  },
  { immediate: true }
);
</script>

<style scoped>
.no-border {
  border: none !important;
  box-shadow: none !important;
}
</style>