<template>
  <v-container>
    <h1 class="text-h4 mb-4">Pesquisa de Produtos</h1>

    <!-- Verificação de usuário cliente -->
    <v-alert v-if="!authStore.isClient" type="error" variant="tonal" class="mb-4">
      Apenas clientes podem acessar esta funcionalidade.
    </v-alert>

    <div v-else>
      <!-- Autocomplete para selecionar produto único -->
      <v-autocomplete
        v-model="selectedProduct"
        :items="productStore.products"
        item-value="id"
        item-title="name"
        label="Pesquisar Produto"
        :loading="productStore.loading"
        clearable
        return-object
        auto-select-first
        no-data-text="Nenhum produto encontrado"
        @update:search="debouncedSearch"
        class="mb-4"
      >
        <template v-slot:item="{ props, item }">
          <v-list-item v-bind="props" :title="null">
            <template v-slot:prepend>
              <v-img :src="imageUrl(item.raw.image)" width="40" height="40" class="mr-2" cover></v-img>
            </template>
            <v-list-item-title class="font-weight-bold">
              {{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit }}
            </v-list-item-title>
            <v-list-item-subtitle>
              <span class="d-block">Peso: {{ item.raw.quantity }} {{ item.raw.weight_unit }}</span>
              <span v-if="item.raw.package_type" class="d-block">Embalagem: {{ item.raw.package_type }}</span>
            </v-list-item-subtitle>
          </v-list-item>
        </template>
        <template v-slot:selection="{ item }">
          <div class="d-flex align-center">
            <v-img :src="imageUrl(item.raw.image)" width="30" height="30" class="mr-2" cover></v-img>
            <span>{{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit }}</span>
          </div>
        </template>
      </v-autocomplete>

      <!-- Botões para pesquisa única -->
      <v-btn
        color="primary"
        class="mt-2 mr-2"
        :disabled="!selectedProduct"
        @click="searchSingleProductPrices"
      >
        Buscar Melhores Preços
      </v-btn>
      <v-btn
        color="secondary"
        class="mt-2"
        :disabled="productStore.storeProducts.length === 0"
        @click="clearSingleProductSearch"
      >
        Limpar Pesquisa
      </v-btn>

      <!-- Checkbox para ativar/desativar lista de compras -->
      <v-checkbox
        v-model="isShoppingListEnabled"
        label="Criar Lista de Compras"
        class="mt-4"
        @change="toggleShoppingList"
      ></v-checkbox>

      <!-- Modal para lista de compras -->
      <v-dialog v-model="shoppingListDialog" max-width="800px">
        <v-card>
          <v-card-title>
            Lista de Compras
            <v-spacer></v-spacer>
            <v-btn
              color="secondary"
              class="mr-2"
              @click="shoppingListDialog = false"
            >
              Fechar
            </v-btn>
            <v-btn
              color="primary"
              class="mt-4"
              :disabled="shoppingListItems.every(item => !item.product || !item.quantity || item.quantity <= 0)"
              @click="searchShoppingList"
            >
              Buscar Melhores Preços
            </v-btn>
          </v-card-title>
          <v-card-text>
            <!-- Linhas dinâmicas para adicionar produtos -->
            <v-row
              v-for="(item, index) in shoppingListItems"
              :key="index"
              class="mb-2 align-center"
            >
              <v-col cols="8">
                <v-autocomplete
                  v-model="item.product"
                  :items="productStore.products"
                  item-value="id"
                  item-title="name"
                  label="Produto"
                  clearable
                  return-object
                  :disabled="!isShoppingListEnabled"
                  @update:modelValue="checkAndAddNewRow(index)"
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="null">
                      <template v-slot:prepend>
                        <v-img :src="imageUrl(item.raw.image)" width="40" height="40" class="mr-2" cover></v-img>
                      </template>
                      <v-list-item-title class="font-weight-bold">
                        {{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit }}
                      </v-list-item-title>
                    </v-list-item>
                  </template>
                  <template v-slot:selection="{ item }">
                    <div class="d-flex align-center">
                      <v-img :src="imageUrl(item.raw.image)" width="30" height="30" class="mr-2" cover></v-img>
                      <span>{{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit }}</span>
                    </div>
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col cols="3">
                <v-text-field
                  v-model.number="item.quantity"
                  label="Quantidade"
                  type="number"
                  min="1"
                  :disabled="!isShoppingListEnabled"
                  :rules="[v => (v && v > 0) || 'Quantidade deve ser maior que zero']"
                  @update:modelValue="checkAndAddNewRow(index)"
                ></v-text-field>
              </v-col>
              <v-col cols="1" v-if="index > 0">
                <v-btn icon color="error" @click="removeRow(index)">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>

            <!-- Botão para buscar preços (duplicado para consistência visual, pode remover um se preferir) -->
            <v-btn
              color="primary"
              class="mt-4"
              :disabled="shoppingListItems.every(item => !item.product || !item.quantity || item.quantity <= 0)"
              @click="searchShoppingList"
            >
              Buscar Melhores Preços
            </v-btn>
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- Mensagem de erro -->
      <v-alert v-if="productStore.error" type="error" variant="tonal" class="mb-4">
        {{ productStore.error }}
      </v-alert>

      <!-- Tabela de resultados da lista de compras ou produto único -->
      <v-data-table
        v-if="productStore.storeProducts.length > 0 || productStore.shoppingListResults.length > 0"
        :headers="storeHeaders"
        :items="sortedStores"
        :loading="productStore.loading"
        class="elevation-1"
        :items-per-page="itemsPerPage"
        v-model:page="page"
        show-expand
        @update:page="handlePageChange"
        @update:items-per-page="handleItemsPerPageChange"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Lojas com Melhores Preços</v-toolbar-title>
          </v-toolbar>
        </template>
        <template v-slot:item.total_price="{ item }">
          {{ formatPrice(item.total_price) }}
        </template>
        <template v-slot:expanded-row="{ columns, item }">
          <tr>
            <td :colspan="columns.length">
              <v-data-table
                :headers="itemHeaders"
                :items="item.items"
                hide-default-footer
              >
                <template v-slot:item.store_product.product.image="{ item }">
                  <v-img :src="imageUrl(item.store_product.product.image)" max-width="50" max-height="50" @error="onImageError(item.store_product)" @click="openImageDialog(item.store_product)" style="cursor: pointer;"></v-img>
                </template>
                <template v-slot:item.store_product.product.name="{ item }">
                  {{ item.store_product.product.name }}
                </template>
                <template v-slot:item.store_product.product.quantity="{ item }">
                  {{ formatQuantity(item.store_product.product.quantity, item.store_product.product.weight_unit) }}
                </template>
                <template v-slot:item.quantity="{ item }">
                  {{ item.quantity }}
                </template>
                <template v-slot:item.item_total="{ item }">
                  {{ formatPrice(item.item_total) }}
                </template>
                <template v-slot:item.store_product.price="{ item }">
                  {{ formatPrice(item.store_product.price) }}
                </template>
                <template v-slot:item.store_product.bulk_price="{ item }">
                  {{ formatPrice(item.store_product.bulk_price) }}
                </template>
                <template v-slot:item.store_product.loyalty_price="{ item }">
                  {{ formatPrice(item.store_product.loyalty_price) }}
                </template>
                <template v-slot:item.store_product.bulk_min_quantity="{ item }">
                  {{ formatQuantity(item.store_product.bulk_min_quantity) }}
                </template>
                <template v-slot:item.store_product.is_active="{ item }">
                  <v-chip :color="item.store_product.is_active ? 'success' : 'error'" small>
                    {{ item.store_product.is_active ? 'Ativo' : 'Inativo' }}
                  </v-chip>
                </template>
              </v-data-table>
            </td>
          </tr>
        </template>
      </v-data-table>

      <!-- Mensagem para quando não há resultados -->
      <v-alert v-else-if="searched && !productStore.loading" type="info" variant="tonal" class="mt-4">
        Nenhuma loja encontrada para o produto ou lista de compras.
      </v-alert>

      <!-- Diálogo para visualizar imagem e detalhes -->
      <v-dialog v-model="imageDialog" max-width="600px">
        <v-card>
          <v-card-title>Detalhes do Produto</v-card-title>
          <v-card-text>
            <v-img :src="imageUrl(selectedStoreProduct?.product?.image)" max-height="300" contain class="mb-4"></v-img>
            <v-row>
              <v-col cols="12">
                <p><strong>Nome:</strong> {{ selectedStoreProduct?.product?.name || 'N/A' }}</p>
                <p><strong>Loja:</strong> {{ selectedStoreProduct?.store_username || 'N/A' }}</p>
                <p><strong>Tipo de Embalagem:</strong> {{ selectedStoreProduct?.product?.package_type || 'N/A' }}</p>
                <p><strong>Quantidade:</strong> {{ formatQuantity(selectedStoreProduct?.product?.quantity, selectedStoreProduct?.product?.weight_unit) }}</p>
                <p><strong>Descrição:</strong> {{ selectedStoreProduct?.product?.description || 'Sem descrição' }}</p>
                <p><strong>Preço:</strong> {{ formatPrice(selectedStoreProduct?.price) }}</p>
                <p v-if="selectedStoreProduct?.bulk_price"><strong>Preço por Quantidade:</strong> {{ formatPrice(selectedStoreProduct?.bulk_price) }}</p>
                <p v-if="selectedStoreProduct?.bulk_min_quantity"><strong>Quantidade Mínima:</strong> {{ formatQuantity(selectedStoreProduct?.bulk_min_quantity) }}</p>
                <p v-if="selectedStoreProduct?.loyalty_price"><strong>Preço por Fidelidade:</strong> {{ formatPrice(selectedStoreProduct?.loyalty_price) }}</p>
                <p><strong>Ativo:</strong> {{ selectedStoreProduct?.is_active ? 'Sim' : 'Não' }}</p>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="secondary" @click="imageDialog = false">Fechar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Snackbar -->
      <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
        {{ snackbarText }}
        <template v-slot:action="{ attrs }">
          <v-btn text v-bind="attrs" @click="snackbar = false">Fechar</v-btn>
        </template>
      </v-snackbar>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useProductStore } from '~/stores/products';
import { useAuthStore } from '~/stores/auth';
import { debounce } from 'lodash';
import { useRouter } from 'vue-router';

interface Product {
  id: number;
  name: string;
  package_type: string;
  quantity: number;
  weight_unit: string;
  description: string;
  image: string | null;
  admin: number;
  created_at: string;
  updated_at: string;
}

interface StoreProduct {
  id: number;
  store: number;
  store_username: string;
  product: Product;
  price: number;
  bulk_price: number | null;
  bulk_min_quantity: number | null;
  loyalty_price: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ShoppingListResult {
  store_id: number;
  store_username: string;
  total_price: number;
  items: {
    store_product: StoreProduct;
    quantity: number;
    item_total: number;
  }[];
}

const productStore = useProductStore();
const authStore = useAuthStore();
const router = useRouter();

const selectedProduct = ref<Product | null>(null);
const quantity = ref<number>(1);
const isShoppingListEnabled = ref(false);
const shoppingListDialog = ref(false);
const imageDialog = ref(false);
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const selectedStoreProduct = ref<StoreProduct | null>(null);
const page = ref(1);
const itemsPerPage = ref(10);
const baseUrl = ref('http://localhost:8000');
const shoppingListItems = ref<{ product: Product | null; quantity: number | null }[]>([{ product: null, quantity: null }]);
const searched = ref(false);

// Cabeçalhos da tabela de lojas
const storeHeaders = [
  { title: 'Loja', key: 'store_username' },
  
  { title: 'Itens Encontrados na Loja', key: 'store_item_count', sortable: true },
  { title: 'Preço Total', key: 'total_price', sortable: true },
];

// Cabeçalhos da tabela de itens (expansão)
const itemHeaders = [
  { title: 'Imagem', key: 'store_product.product.image', sortable: false },
  { title: 'Produto', key: 'store_product.product.name' },
  { title: 'Peso', key: 'store_product.product.quantity' },
  { title: 'Quantidade', key: 'quantity' },
  { title: 'Preço Unitário', key: 'store_product.price' },
  { title: 'Preço por Quantidade', key: 'store_product.bulk_price' },
  { title: 'Quantidade Mínima', key: 'store_product.bulk_min_quantity' },
  { title: 'Preço por Fidelidade', key: 'store_product.loyalty_price' },
  { title: 'Total Item', key: 'item_total' },
  { title: 'Ativo', key: 'store_product.is_active' },
];

// Função para formatar URLs de imagens
const imageUrl = computed(() => {
  return (image: string | undefined) => {
    if (!image) return '/placeholder.png';
    if (image.startsWith('http://') || image.startsWith('https://')) {
      return image;
    }
    const cleanImagePath = image.startsWith('/') ? image.slice(1) : image;
    return `${baseUrl.value}/media/${cleanImagePath}`;
  };
});

// Função para ordenar lojas por quantidade de itens e preço
const sortedStores = computed(() => {
  // Quantidade solicitada pelo cliente (soma das quantidades da lista de compras)
  const clientRequestedCount = shoppingListItems.value
    .filter(item => item.product && item.quantity && item.quantity > 0)
    .reduce((sum, item) => sum + (item.quantity || 0), 0);

  const items = productStore.shoppingListResults.length > 0
    ? productStore.shoppingListResults.map(result => ({
        ...result,
        client_requested_count: clientRequestedCount, // Quantidade total que o cliente quer comprar
        store_item_count: result.items.length, // Número de itens da lista que a loja tem
      }))
    : productStore.storeProducts.map(sp => ({
        store_username: sp.store_username,
        total_price: sp.price,
        items: [{ store_product: sp, quantity: 1, item_total: sp.price }],
        client_requested_count: 1, // Para pesquisa única, quantidade é 1
        store_item_count: 1, // Para pesquisa única, assume 1 item
      }));

  return items.sort((a, b) => {
    const countDiff = b.store_item_count - a.store_item_count; // Prioriza lojas com mais itens encontrados
    if (countDiff !== 0) return countDiff;
    return a.total_price - b.total_price; // Em caso de empate, menor preço
  });
});

// Função de busca com debounce
const debouncedSearch = debounce(async (search: string) => {
  if (search.trim()) {
    await productStore.fetchClientProductSearch(search);
  } else {
    await productStore.fetchClientProductSearch(''); // Garante que a lista inicial seja carregada
  }
}, 500);

// Função para alternar a lista de compras
function toggleShoppingList() {
  if (isShoppingListEnabled.value && !shoppingListDialog.value) {
    shoppingListDialog.value = true;
    if (productStore.products.length === 0) {
      productStore.fetchClientProductSearch(''); // Carrega produtos se ainda não carregados
    }
  } else if (!isShoppingListEnabled.value) {
    shoppingListDialog.value = false;
    shoppingListItems.value = [{ product: null, quantity: null }];
    searched.value = false;
    productStore.shoppingListResults = [];
  }
}

// Função para buscar preços de um único produto
async function searchSingleProductPrices() {
  if (!selectedProduct.value) return;

  try {
    await productStore.fetchClientStoreProducts(selectedProduct.value.id);
    searched.value = true;
    snackbarText.value = 'Preços buscados com sucesso!';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (err: any) {
    snackbarText.value = err.data?.detail || 'Erro ao buscar preços. Tente novamente.';
    snackbarColor.value = 'error';
    snackbar.value = true;
  }
}

// Função para limpar a pesquisa de um único produto
function clearSingleProductSearch() {
  selectedProduct.value = null;
  productStore.storeProducts = [];
  searched.value = false;
  snackbarText.value = 'Pesquisa limpa!';
  snackbarColor.value = 'info';
  snackbar.value = true;
}

// Função para verificar e adicionar nova linha
function checkAndAddNewRow(index: number) {
  const item = shoppingListItems.value[index];
  if (item.product && item.quantity && item.quantity > 0) {
    if (index === shoppingListItems.value.length - 1) {
      shoppingListItems.value.push({ product: null, quantity: null });
    }
  }
}

// Função para remover uma linha
function removeRow(index: number) {
  if (shoppingListItems.value.length > 1) {
    shoppingListItems.value.splice(index, 1);
  }
}

// Função para buscar preços da lista de compras
async function searchShoppingList() {
  const validItems = shoppingListItems.value.filter(item => item.product && item.quantity && item.quantity > 0);
  if (validItems.length === 0) return;

  const items = validItems.map(item => ({
    product_id: item.product.id,
    quantity: item.quantity,
  }));

  try {
    await productStore.fetchShoppingList(items);
    searched.value = true;
    shoppingListDialog.value = false;
    snackbarText.value = 'Lista de compras processada com sucesso!';
    snackbarColor.value = 'success';
    snackbar.value = true;
  } catch (err: any) {
    snackbarText.value = err.data?.detail || 'Erro ao processar lista de compras. Tente novamente.';
    snackbarColor.value = 'error';
    snackbar.value = true;
  }
}

// Manipuladores de paginação
const handlePageChange = (newPage: number) => {
  page.value = newPage;
};

const handleItemsPerPageChange = (newItemsPerPage: number) => {
  itemsPerPage.value = newItemsPerPage;
  page.value = 1;
};

// Funções de formatação
function formatPrice(price: number | string | null): string {
  if (price === null || price === undefined) return 'N/A';
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return `R$ ${numPrice.toFixed(2).replace('.', ',')}`;
}

function formatQuantity(quantity: number | string | null, unit: string | null = null): string {
  if (quantity === null || quantity === undefined) return '-';
  const numericQuantity = Number(quantity);
  const formattedValue = Math.floor(numericQuantity).toString();
  const formattedUnit = unit && unit.toLowerCase() === 'l' ? 'L' : (unit || '').toLowerCase();
  return formattedUnit ? `${formattedValue}${formattedUnit}` : formattedValue;
}

function onImageError(item: StoreProduct) {
  console.error(`Erro ao carregar imagem para o produto ${item.product?.name}: ${item.product?.image}`);
}

function openImageDialog(item: StoreProduct) {
  selectedStoreProduct.value = { ...item };
  imageDialog.value = true;
}

// Carregar produtos iniciais ao montar
onMounted(() => {
  if (!authStore.isClient) {
    router.push('/');
  } else if (productStore.products.length === 0) {
    productStore.fetchClientProductSearch(''); // Garante que os produtos sejam carregados ao abrir
  }
});
</script>

<style scoped>
.v-data-table {
  border-radius: 0;
  border: none;
}

.v-chip {
  font-weight: 500;
}

.v-btn {
  text-transform: none;
}
</style>