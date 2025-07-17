<template>
  <v-container>
    <h1 class="text-h4 mb-6">
      <v-icon left>mdi-store</v-icon>
      Produtos por Loja
    </h1>

    <!-- Seletor de Loja -->
    <v-card class="mb-6">
      <v-card-title>
        <v-select
          v-model="selectedStore"
          :items="stores"
          item-value="id"
          item-title="username"
          label="Selecione uma loja"
          prepend-inner-icon="mdi-store"
          clearable
          :loading="loadingStores"
          :disabled="loadingStores"
          @update:modelValue="loadStoreProducts"
        ></v-select>
      </v-card-title>
    </v-card>

    <!-- Indicador de Carregamento -->
    <v-progress-circular
      v-if="loadingProducts"
      indeterminate
      color="primary"
      class="mb-6"
    ></v-progress-circular>

    <!-- Mensagem para nenhuma loja selecionada -->
    <v-alert
      v-else-if="!selectedStore"
      type="info"
      class="mb-6"
    >
      Selecione uma loja para visualizar seus produtos.
    </v-alert>

    <!-- Mensagem para loja sem produtos -->
    <v-alert
      v-else-if="selectedStore && storeProducts.length === 0"
      type="info"
      class="mb-6"
    >
      Nenhum produto encontrado para esta loja.
    </v-alert>

    <!-- Pesquisa e Total de Itens -->
    <v-card v-else-if="selectedStore && storeProducts.length > 0" class="mb-6">
      <v-card-text class="d-flex align-center justify-space-between">
        <v-text-field
          v-model="tableSearch"
          label="Pesquisar produtos"
          prepend-inner-icon="mdi-magnify"
          clearable
          style="max-width: 300px;"
          @input="updateVisibleItemsCount"
        ></v-text-field>
        <div>
          <v-chip color="primary" class="font-weight-bold mr-2">
            Itens: {{ visibleItemsCount }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>

    <!-- Tabela de Produtos -->
    <v-data-table
      v-if="selectedStore && storeProducts.length > 0"
      ref="dataTable"
      :headers="productHeaders"
      :items="storeProducts"
      :loading="loadingProducts"
      :search="tableSearch"
      :items-per-page="-1"
      :custom-filter="customFilter"
      class="elevation-1"
      @update:page="updateVisibleItemsCount"
      @update:items-per-page="updateVisibleItemsCount"
    >
      <template v-slot:item.image="{ item }">
        <v-img
          :src="getImageUrl(item.product?.image)"
          max-width="50"
          max-height="50"
          contain
        ></v-img>
      </template>
      <template v-slot:item.price="{ item }">
        {{ formatPrice(item.price) }}
      </template>
      <template v-slot:item.bulk_price="{ item }">
        {{ formatPrice(item.bulk_price) }}
      </template>
      <template v-slot:item.loyalty_price="{ item }">
        {{ formatPrice(item.loyalty_price) }}
      </template>
      <template v-slot:item.bulk_min_quantity="{ item }">
        {{ formatQuantity(item.bulk_min_quantity) }}
      </template>
      <template v-slot:item.is_active="{ item }">
        <v-chip :color="item.is_active ? 'success' : 'error'" small>
          {{ item.is_active ? 'Ativo' : 'Inativo' }}
        </v-chip>
      </template>
    </v-data-table>

    <!-- Snackbar para mensagens -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();
const dataTable = ref(null);

// Dados
const stores = ref([]);
const selectedStore = ref(null);
const storeProducts = ref([]);
const loadingStores = ref(false);
const loadingProducts = ref(false);
const tableSearch = ref('');
const visibleItemsCount = ref(0);

// Snackbar
const snackbar = ref({
  show: false,
  color: 'success',
  message: '',
});

// Cabeçalhos da tabela
const baseHeaders = [
  { title: 'Imagem', key: 'image', sortable: false },
  { title: 'Produto', key: 'product.name', sortable: true },
  { title: 'Preço', key: 'price', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
];

const productHeaders = computed(() => {
  const headers = [...baseHeaders];
  
  if (storeProducts.value.some(p => p.bulk_price !== null)) {
    headers.splice(3, 0, { title: 'Preço Qtd.', key: 'bulk_price', sortable: true });
  }
  
  if (storeProducts.value.some(p => p.loyalty_price !== null)) {
    headers.splice(4, 0, { title: 'Preço Fidelidade', key: 'loyalty_price', sortable: true });
  }
  
  if (storeProducts.value.some(p => p.bulk_min_quantity !== null)) {
    headers.splice(3, 0, { title: 'Qtd. Mínima', key: 'bulk_min_quantity', sortable: true });
  }

  return headers;
});

// Filtro personalizado
const customFilter = (value, query, item) => {
  if (!query) return true;
  const normalizedQuery = query.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const productName = item.raw.product?.name?.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '') || '';
  return productName.includes(normalizedQuery);
};

// Atualiza contagem de itens visíveis
const updateVisibleItemsCount = () => {
  if (!dataTable.value) return;
  
  setTimeout(() => {
    const rows = dataTable.value.$el.querySelectorAll('tbody tr:not(.v-data-table__no-data)');
    visibleItemsCount.value = rows.length;
  }, 50);
};

// Carrega lojas
const loadStores = async () => {
  if (!authStore.isAdmin) {
    showSnackbar('Acesso não autorizado', 'error');
    router.push('/');
    return;
  }

  try {
    loadingStores.value = true;
    await authStore.fetchAllUsers();
    stores.value = authStore.users.filter(user => user.user_type === 'store');
  } catch (error) {
    showSnackbar('Erro ao carregar lojas', 'error');
    console.error('Erro ao carregar lojas:', error);
  } finally {
    loadingStores.value = false;
  }
};

// Carrega produtos da loja
const loadStoreProducts = async (storeId) => {
  if (!storeId) {
    storeProducts.value = [];
    tableSearch.value = '';
    visibleItemsCount.value = 0;
    return;
  }

  try {
    loadingProducts.value = true;
    const url = `${useRuntimeConfig().public.apiBase}/store-products/?store_id=${storeId}`;
    const response = await $fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
    });

    storeProducts.value = Array.isArray(response) ? response.map(product => ({
      ...product,
      product: product.product || { name: 'Desconhecido', brand: 'N/A', image: null },
      price: product.price ? Number(product.price) : 0,
      bulk_price: product.bulk_price ? Number(product.bulk_price) : null,
      loyalty_price: product.loyalty_price ? Number(product.loyalty_price) : null,
      bulk_min_quantity: product.bulk_min_quantity ? Number(product.bulk_min_quantity) : null,
      store: product.store || null,
    })) : [];
    
    // Atualiza a contagem após carregar os produtos
    setTimeout(updateVisibleItemsCount, 100);
  } catch (error) {
    showSnackbar('Erro ao carregar produtos da loja', 'error');
    console.error('Erro ao carregar produtos:', error);
    storeProducts.value = [];
    visibleItemsCount.value = 0;
  } finally {
    loadingProducts.value = false;
  }
};

// Formatações
const getImageUrl = (imagePath) => {
  if (!imagePath) return '/default-product.png';
  if (imagePath.startsWith('http')) return imagePath;
  return `${useRuntimeConfig().public.apiBase}/storage/${imagePath}`;
};

const formatPrice = (price) => {
  if (price === null || price === undefined) return '-';
  return `R$ ${Number(price).toFixed(2).replace('.', ',')}`;
};

const formatQuantity = (quantity) => {
  if (quantity === null || quantity === undefined) return '-';
  return quantity.toString();
};

const showSnackbar = (message, color) => {
  snackbar.value = {
    show: true,
    message,
    color,
  };
};

// Watchers
watch(selectedStore, (newStoreId) => {
  loadStoreProducts(newStoreId);
});

watch(tableSearch, () => {
  updateVisibleItemsCount();
});

// Inicialização
onMounted(async () => {
  await loadStores();
});
</script>

<style scoped>
.v-data-table {
  border-radius: 0;
  border: none;
}
</style>