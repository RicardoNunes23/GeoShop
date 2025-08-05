<template>
  <v-container>
    <h1 class="text-h4 mb-4">Pesquisa de Produtos</h1>

    <VueLeaflet 
      :stores="storeMarkers" 
      :userLocation="userLocation"
      @marker-click="onStoreMarkerClick"
      class="mb-4"
      v-if="showMap"
    />

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
        :key="autocompleteKey"
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
        :disabled="productStore.storeProducts.length === 0 && productStore.shoppingListResults.length === 0"
        @click="clearSearch"
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

      <!-- Tabela de resultados -->
      <v-data-table
        v-if="productStore.storeProducts.length > 0 || productStore.shoppingListResults.length > 0"
        :headers="storeHeaders"
        :items="sortedStores"
        :loading="productStore.loading"
        class="elevation-1 mt-4"
        :items-per-page="itemsPerPage"
        v-model:page="page"
        show-expand
        @update:page="handlePageChange"
        @update:items-per-page="handleItemsPerPageChange"
      >
        <template v-slot:top>
          <v-toolbar flat>
            <v-toolbar-title>Lojas com Melhores Preços</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              @click="showMap = !showMap"
              class="mr-2"
            >
              {{ showMap ? 'Ocultar Mapa' : 'Mostrar Mapa' }}
            </v-btn>
          </v-toolbar>
        </template>
        <template v-slot:item.store_username="{ item }">
          <a href="#" @click.prevent="focusOnStore(item)">{{ item.store_username }}</a>
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
                  <v-img 
                    :src="imageUrl(item.store_product.product.image)" 
                    max-width="50" 
                    max-height="50" 
                    @error="onImageError(item.store_product)" 
                    @click="openImageDialog(item.store_product)" 
                    style="cursor: pointer;"
                  ></v-img>
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

      <v-alert v-else-if="searched && !productStore.loading" type="info" variant="tonal" class="mt-4">
        Nenhuma loja encontrada para o produto ou lista de compras.
      </v-alert>

      <v-dialog v-model="imageDialog" max-width="600px">
        <v-card>
          <v-card-title>Detalhes do Produto</v-card-title>
          <v-card-text>
            <v-img 
              :src="imageUrl(selectedStoreProduct?.product?.image)" 
              max-height="300" 
              contain 
              class="mb-4"
            ></v-img>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useProductStore } from '~/stores/products';
import { useAuthStore } from '~/stores/auth';
import { useGeolocation } from '@vueuse/core';
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
  store_latitude?: number | null;
  store_longitude?: number | null;
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
  store_latitude?: number | null;
  store_longitude?: number | null;
}

const productStore = useProductStore();
const authStore = useAuthStore();
const router = useRouter();
const { coords } = useGeolocation();

const selectedProduct = ref<Product | null>(null);
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
const showMap = ref(false);
const userLocation = ref<[number, number] | null>(null);
const autocompleteKey = ref(0);

const storeHeaders = [
  { title: 'Loja', key: 'store_username' },
  { title: 'Itens Encontrados', key: 'store_item_count', sortable: true },
  { title: 'Preço Total', key: 'total_price', sortable: true },
  { title: 'Distância', key: 'distance', sortable: true },
];

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

const storeMarkers = computed(() => {
  if (!productStore.storeProducts.length && !productStore.shoppingListResults.length) {
    console.log('Nenhum dado em storeProducts ou shoppingListResults');
    return [];
  }

  const stores = productStore.shoppingListResults.length > 0 
    ? productStore.shoppingListResults
    : productStore.storeProducts.map(sp => ({
        store_id: sp.store,
        store_username: sp.store_username,
        total_price: sp.price,
        items: [{ store_product: sp, quantity: 1, item_total: sp.price }],
        store_latitude: sp.store_latitude,
        store_longitude: sp.store_longitude
      }));

  console.log('Stores processados:', stores);

  // Calcular o número total de produtos solicitados na lista de compras
  const requestedItemsCount = productStore.shoppingListResults.length > 0
    ? shoppingListItems.value.filter(item => item.product && item.quantity && item.quantity > 0).length
    : 1;

  // Calcular preços mínimo e máximo entre lojas com todos os produtos solicitados
  const completeStores = stores.filter(store => store.items.length === requestedItemsCount);
  const prices = completeStores.length > 0
    ? completeStores.map(store => store.total_price).filter(price => price !== null && price !== undefined)
    : stores.map(store => store.total_price).filter(price => price !== null && price !== undefined);
  const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;

  const markers = stores
    .map(store => {
      const authStoreUser = authStore.users.find(
        user => user.id === store.store_id && user.user_type === 'store'
      );
      const hasValidCoords = 
        (authStoreUser?.latitude && authStoreUser?.longitude) || 
        (store.store_latitude !== null && store.store_latitude !== undefined && 
         store.store_longitude !== null && store.store_longitude !== undefined);

      console.log(`Loja ${store.store_username}:`, {
        hasValidCoords,
        authStoreUserCoords: authStoreUser ? { latitude: authStoreUser.latitude, longitude: authStoreUser.longitude } : null,
        storeCoords: { store_latitude: store.store_latitude, store_longitude: store.store_longitude }
      });

      const lat = authStoreUser?.latitude ?? store.store_latitude;
      const lng = authStoreUser?.longitude ?? store.store_longitude;

      if (!hasValidCoords) {
        console.warn(`Loja ${store.store_username} não possui coordenadas válidas`, {
          authStoreUser,
          productStoreData: store
        });
        return null;
      }

      let distance = null;
      if (userLocation.value && lat !== null && lng !== null) {
        distance = calculateDistance(
          userLocation.value[0], 
          userLocation.value[1],
          lat,
          lng
        );
      }

      return {
        id: store.store_id || store.items[0]?.store_product?.store,
        name: store.store_username,
        latLng: [lat, lng] as [number, number],
        total_price: formatPrice(store.total_price),
        items_count: store.items?.length || 1,
        distance: distance,
        iconUrl: getMarkerIcon(store.total_price, store.items.length, requestedItemsCount, minPrice, maxPrice),
        hasValidCoords
      };
    })
    .filter(store => store !== null);

  console.log('Marcadores gerados:', markers);
  return markers;
});

const sortedStores = computed(() => {
  const clientRequestedCount = shoppingListItems.value
    .filter(item => item.product && item.quantity && item.quantity > 0)
    .reduce((sum, item) => sum + (item.quantity || 0), 0);

  const items = productStore.shoppingListResults.length > 0
    ? productStore.shoppingListResults.map(result => {
        let distance = null;
        if (userLocation.value && result.store_latitude && result.store_longitude) {
          distance = calculateDistance(
            userLocation.value[0],
            userLocation.value[1],
            result.store_latitude,
            result.store_longitude
          );
        }

        return {
          ...result,
          client_requested_count: clientRequestedCount,
          store_item_count: result.items.length,
          distance: distance
        };
      })
    : productStore.storeProducts.map(sp => {
        let distance = null;
        if (userLocation.value && sp.store_latitude && sp.store_longitude) {
          distance = calculateDistance(
            userLocation.value[0],
            userLocation.value[1],
            sp.store_latitude,
            sp.store_longitude
          );
        }

        return {
          store_username: sp.store_username,
          total_price: sp.price,
          items: [{ store_product: sp, quantity: 1, item_total: sp.price }],
          client_requested_count: 1,
          store_item_count: 1,
          distance: distance,
          store_latitude: sp.store_latitude,
          store_longitude: sp.store_longitude
        };
      });

  return items.sort((a, b) => {
    // Priorizar lojas com mais itens correspondentes
    const countDiff = b.store_item_count - a.store_item_count;
    if (countDiff !== 0) return countDiff;
    // Se o número de itens for igual, ordenar por preço
    return a.total_price - b.total_price;
  });
});

const debouncedSearch = debounce(async (search: string) => {
  if (search.trim()) {
    await productStore.fetchClientProductSearch(search);
  } else {
    await productStore.fetchClientProductSearch('');
  }
}, 500);

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Raio da Terra em km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return parseFloat((R * c).toFixed(2));
}

function getMarkerIcon(price: number | undefined, itemsCount: number, requestedItemsCount: number, minPrice: number, maxPrice: number): string {
  if (!price) return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png';

  console.log(`getMarkerIcon: price=${price}, itemsCount=${itemsCount}, requestedItemsCount=${requestedItemsCount}, minPrice=${minPrice}, maxPrice=${maxPrice}`);

  // Para pesquisa de produto único (requestedItemsCount === 1), manter a lógica baseada apenas no preço
  if (requestedItemsCount === 1) {
    if (minPrice === maxPrice) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png';
    }
    const priceRange = maxPrice - minPrice;
    const cheapThreshold = minPrice + priceRange * 0.33;
    const expensiveThreshold = minPrice + priceRange * 0.66;
    if (price <= cheapThreshold) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png';
    } else if (price >= expensiveThreshold) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png';
    } else {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png';
    }
  }

  // Para lista de compras, priorizar lojas com todos os produtos solicitados
  if (itemsCount === requestedItemsCount) {
    if (minPrice === maxPrice) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png';
    }
    const priceRange = maxPrice - minPrice;
    const cheapThreshold = minPrice + priceRange * 0.33;
    const expensiveThreshold = minPrice + priceRange * 0.66;
    if (price <= cheapThreshold) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png';
    } else if (price >= expensiveThreshold) {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png';
    } else {
      return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png';
    }
  } else {
    return 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png';
  }
}

async function searchSingleProductPrices() {
  if (!selectedProduct.value) return;

  try {
    await productStore.fetchClientStoreProducts(selectedProduct.value.id);
    searched.value = true;
    showMap.value = true;
    showSuccess('Preços buscados com sucesso!');
  } catch (err: any) {
    showError(err.data?.detail || 'Erro ao buscar preços. Tente novamente.');
  }
}

async function searchShoppingList() {
  const validItems = shoppingListItems.value.filter(item => item.product && item.quantity && item.quantity > 0);
  if (validItems.length === 0) return;

  const items = validItems.map(item => ({
    product_id: item.product!.id,
    quantity: item.quantity!,
  }));

  try {
    await productStore.fetchShoppingList(items);
    searched.value = true;
    showMap.value = true;
    shoppingListDialog.value = false;
    showSuccess('Lista de compras processada com sucesso!');
  } catch (err: any) {
    showError(err.data?.detail || 'Erro ao processar lista de compras. Tente novamente.');
  }
}

function clearSearch() {
  console.log('Iniciando clearSearch');
  selectedProduct.value = null;
  productStore.storeProducts = [];
  productStore.shoppingListResults = [];
  shoppingListItems.value = [{ product: null, quantity: null }];
  isShoppingListEnabled.value = false;
  shoppingListDialog.value = false;
  searched.value = false;
  showMap.value = false;
  productStore.error = null;
  showInfo('Pesquisa limpa!');
  autocompleteKey.value++;
  console.log('Estado após limpeza:', {
    selectedProduct: selectedProduct.value,
    storeProducts: productStore.storeProducts,
    shoppingListResults: productStore.shoppingListResults,
    shoppingListItems: shoppingListItems.value,
    isShoppingListEnabled: isShoppingListEnabled.value,
    shoppingListDialog: shoppingListDialog.value,
    searched: searched.value,
    showMap: showMap.value,
    productStoreError: productStore.error
  });
  if (productStore.products.length === 0) {
    productStore
      .fetchClientProductSearch('')
      .then(() => {
        console.log('Produtos recarregados:', productStore.products);
      })
      .catch(err => {
        console.error('Erro ao recarregar produtos:', err);
        showError('Erro ao recarregar produtos. Tente novamente.');
      });
  } else {
    console.log('Produtos já carregados:', productStore.products);
  }
}

function toggleShoppingList() {
  if (isShoppingListEnabled.value && !shoppingListDialog.value) {
    shoppingListDialog.value = true;
    if (productStore.products.length === 0) {
      productStore.fetchClientProductSearch('');
    }
  } else if (!isShoppingListEnabled.value) {
    shoppingListDialog.value = false;
    shoppingListItems.value = [{ product: null, quantity: null }];
    searched.value = false;
    productStore.shoppingListResults = [];
    showMap.value = false;
  }
}

function checkAndAddNewRow(index: number) {
  const item = shoppingListItems.value[index];
  if (item.product && item.quantity && item.quantity > 0) {
    if (index === shoppingListItems.value.length - 1) {
      shoppingListItems.value.push({ product: null, quantity: null });
    }
  }
}

function removeRow(index: number) {
  if (shoppingListItems.value.length > 1) {
    shoppingListItems.value.splice(index, 1);
  }
}

function onStoreMarkerClick(store: any) {
  const storeInTable = sortedStores.value.find(s => 
    s.store_id === store.id || 
    s.store_username === store.name
  );
  if (storeInTable) {
    // Você pode adicionar lógica para destacar a loja na tabela
  }
}

function focusOnStore(store: any) {
  showMap.value = true;
  // Você pode emitir um evento para o componente do mapa focar nesta loja
}

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

function showSuccess(message: string) {
  snackbarText.value = message;
  snackbarColor.value = 'success';
  snackbar.value = true;
}

function showError(message: string) {
  snackbarText.value = message;
  snackbarColor.value = 'error';
  snackbar.value = true;
}

function showInfo(message: string) {
  snackbarText.value = message;
  snackbarColor.value = 'info';
  snackbar.value = true;
}

const handlePageChange = (newPage: number) => {
  page.value = newPage;
};

const handleItemsPerPageChange = (newItemsPerPage: number) => {
  itemsPerPage.value = newItemsPerPage;
  page.value = 1;
};

watch(() => coords.value, (newCoords) => {
  if (newCoords.latitude && newCoords.longitude) {
    userLocation.value = [newCoords.latitude, newCoords.longitude];
  }
}, { immediate: true });

watch(() => productStore.products, () => {
  if (!selectedProduct.value && productStore.products.length > 0) {
    selectedProduct.value = null;
  }
});

onMounted(() => {
  console.log('authStore.users:', authStore.users);
  if (!authStore.isClient) {
    router.push('/');
  } else if (productStore.products.length === 0) {
    productStore.fetchClientProductSearch('');
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

.store-link {
  color: inherit;
  text-decoration: none;
}

.store-link:hover {
  text-decoration: underline;
  color: primary;
}
</style>