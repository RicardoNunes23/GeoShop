<template>
  <v-container>
    <h1 class="text-h4 mb-6">
      <v-icon left>mdi-store</v-icon>
      Produtos por Loja
    </h1>

    <!-- Seletor de Loja -->
   
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
  

    <!-- Exibir dados da loja selecionada -->
    <v-card v-if="selectedStore && selectedStoreData" class="mb-6" elevation="2">
      <v-card-title class="text-h6">
        <v-icon left color="primary">mdi-information-outline</v-icon>
        Dados da Loja
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <v-list-item>
              <v-list-item-title>
                <strong>Nome:</strong> {{ selectedStoreData.username }}
              </v-list-item-title>
            </v-list-item>
          </v-col>
          <v-col cols="12" sm="6">
            <v-list-item>
              <v-list-item-title>
                <strong>Plano:</strong> {{ selectedStoreData.active_plan?.name || 'N/A' }}
              </v-list-item-title>
            </v-list-item>
          </v-col>
          <v-col cols="12" sm="6">
            <v-list-item>
              <v-list-item-title>
                <strong>Limite de Produtos:</strong> {{ selectedStoreData.active_plan?.product_limit || 'N/A' }}
              </v-list-item-title>
            </v-list-item>
          </v-col>
          <v-col cols="12" sm="6">
            <v-list-item>
              <v-list-item-title>
                <strong>Status:</strong>
                <v-chip
                  :color="selectedStoreData.active_plan?.ativo ? 'success' : 'error'"
                  :prepend-icon="selectedStoreData.active_plan?.ativo ? 'mdi-check-circle' : 'mdi-close-circle'"
                  size="small"
                  class="ml-2"
                >
                  {{ selectedStoreData.active_plan?.ativo ? 'Ativo' : 'Inativo' }}
                </v-chip>
              </v-list-item-title>
            </v-list-item>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Mensagem para nenhuma loja selecionada -->
    <v-alert
      v-if="!loadingProducts && !selectedStore"
      type="info"
      class="mb-6"
    >
      Selecione uma loja para visualizar seus produtos.
    </v-alert>

    <!-- Tabela de Produtos -->
    <AppDataTable
      v-if="selectedStore && storeProducts.length > 0"
      :headers="productHeaders"
      :items="filteredProducts"
      :loading="loadingProducts"
      :search="searchQuery"
      :items-per-page="itemsPerPage"
      v-model:page="page"
      :show-item-count="true"
      searchable
      @update:page="handlePageChange"
      @update:items-per-page="handleItemsPerPageChange"
      @update:search="searchQuery = $event"
    >
      <template v-slot:item.image="{ item }">
        <v-img
          :src="getImageUrl(item.product?.image)"
          max-width="50"
          max-height="50"
          contain
        ></v-img>
      </template>
      <template v-slot:item.product.name="{ item }">
        {{ item.product.name }} - {{ formatQuantity(item.product.quantity, item.product.weight_unit) }}
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
        {{ formatQuantity(item.bulk_min_quantity, '') }}
      </template>
      <template v-slot:item.is_active="{ item }">
        <v-chip :color="item.is_active ? 'success' : 'error'" small>
          {{ item.is_active ? 'Ativo' : 'Inativo' }}
        </v-chip>
      </template>
    </AppDataTable>  

    <!-- Snackbar para mensagens -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar.show = false">Fechar</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';
import AppDataTable from '~/components/AppDataTable.vue';

const router = useRouter();
const authStore = useAuthStore();

// Dados
const stores = ref([]);
const selectedStore = ref(null);
const storeProducts = ref([]);
const loadingStores = ref(false);
const loadingProducts = ref(false);
const searchQuery = ref('');
const page = ref(1);
const itemsPerPage = ref(10);

// Snackbar
const snackbar = ref({
  show: false,
  color: 'success',
  message: '',
});

// Propriedade computada para obter dados da loja selecionada
const selectedStoreData = computed(() => {
  return stores.value.find(store => store.id === selectedStore.value) || null;
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

// Produtos filtrados
const filteredProducts = computed(() => {
  if (!searchQuery.value) return storeProducts.value;
  
  return storeProducts.value.filter(product => {
    const query = searchQuery.value.toLowerCase();
    const name = product.product?.name?.toLowerCase() || '';
    const quantityStr = product.product?.quantity ? 
      `${product.product.quantity}${product.product.weight_unit || ''}`.toLowerCase() : '';
    
    return (
      name.includes(query) ||
      quantityStr.includes(query)
    );
  });
});

// Calcula total de páginas
const totalPages = computed(() => {
  if (itemsPerPage.value === -1) {
    return 1;
  }
  return Math.ceil(filteredProducts.value.length / itemsPerPage.value);
});

// Manipuladores de paginação
const handlePageChange = (newPage) => {
  page.value = newPage;
};

const handleItemsPerPageChange = (newItemsPerPage) => {
  itemsPerPage.value = newItemsPerPage;
  page.value = 1;
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
    searchQuery.value = '';
    page.value = 1;
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
    
    // Resetar paginação ao carregar novos produtos
    page.value = 1;
  } catch (error) {
    showSnackbar('Erro ao carregar produtos da loja', 'error');
    console.error('Erro ao carregar produtos:', error);
    storeProducts.value = [];
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

function formatQuantity(quantity, unit) {
  if (quantity === null || quantity === undefined) return '-';
  
  const numericQuantity = Number(quantity);
  const formattedValue = Math.floor(numericQuantity).toString();
  const formattedUnit = unit && unit.toLowerCase() === 'l' ? 'L' : (unit || '').toLowerCase();
  return formattedUnit ? `${formattedValue}${formattedUnit}` : formattedValue;
}

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

.v-pagination {
  justify-content: center;
}

.v-card {
  border-radius: 8px;
}

.v-list-item-title {
  font-size: 1rem;
  line-height: 1.5;
}

.v-chip {
  font-weight: 500;
}
</style>