<template>
  <v-container class="pagination-container">
    <v-row align="center" justify="center">
      <!-- Seleção de itens por página -->
      <v-col cols="auto">
        <v-select
          v-model="localItemsPerPage"
          :items="itemsPerPageOptions"
          label="Itens por página"
          dense
          outlined
          hide-details
          class="items-per-page-select"
          @update:modelValue="updateItemsPerPage"
        ></v-select>
      </v-col>

      <!-- Navegação de páginas -->
      <v-col cols="auto">
        <v-pagination
          v-model="localPage"
          :length="totalPages"
          :total-visible="7"
          prev-icon="mdi-chevron-left"
          next-icon="mdi-chevron-right"
          @update:modelValue="updatePage"
        ></v-pagination>
      </v-col>

      <!-- Contagem de itens -->
      <v-col cols="auto" class="item-count">
        <span>
          {{ startItem }}-{{ endItem }} de {{ totalItems }} itens
        </span>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { computed, ref, watch } from 'vue';

// Propriedades recebidas
const props = defineProps({
  page: {
    type: Number,
    required: true,
  },
  itemsPerPage: {
    type: Number,
    required: true,
  },
  totalItems: {
    type: Number,
    required: true,
  },
});

// Emite eventos para atualização
const emit = defineEmits(['update:page', 'update:items-per-page']);

// Estado local sincronizado com as props
const localPage = ref(props.page);
const localItemsPerPage = ref(props.itemsPerPage);

// Opções de itens por página
const itemsPerPageOptions = [
  { title: '5', value: 5 },
  { title: '10', value: 10 },
  { title: '25', value: 25 },
  { title: '50', value: 50 },
  { title: 'Todos', value: -1 },
];

// Calcula o total de páginas
const totalPages = computed(() => {
  if (localItemsPerPage.value === -1) return 1;
  return Math.ceil(props.totalItems / localItemsPerPage.value);
});

// Calcula o índice do primeiro item exibido
const startItem = computed(() => {
  if (props.totalItems === 0) return 0;
  return (localPage.value - 1) * localItemsPerPage.value + 1;
});

// Calcula o índice do último item exibido
const endItem = computed(() => {
  if (props.totalItems === 0) return 0;
  if (localItemsPerPage.value === -1) return props.totalItems;
  return Math.min(localPage.value * localItemsPerPage.value, props.totalItems);
});

// Função para emitir atualização da página
const updatePage = (newPage) => {
  localPage.value = newPage;
  emit('update:page', newPage);
};

// Função para emitir atualização de itens por página
const updateItemsPerPage = (newItemsPerPage) => {
  localItemsPerPage.value = newItemsPerPage;
  localPage.value = 1; // Resetar para a primeira página
  emit('update:items-per-page', newItemsPerPage);
};

// Sincroniza as props com o estado local
watch(() => props.page, (newPage) => {
  localPage.value = newPage;
});
watch(() => props.itemsPerPage, (newItemsPerPage) => {
  localItemsPerPage.value = newItemsPerPage;
});
</script>

<style scoped>
.pagination-container {
  padding: 16px 0;
}

.items-per-page-select {
  max-width: 150px;
}

.item-count {
  font-size: 0.875rem;
  color: #666;
}

.v-pagination {
  justify-content: center;
}
</style>