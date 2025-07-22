<template>
  <v-container>
    <h1>Gerenciamento de Produtos da Loja</h1>
    <v-alert v-if="authStore.activePlan" type="info" variant="tonal" class="mb-4">
      Seu plano atual ({{ authStore.activePlan.description }}) permite até
      {{ authStore.activePlan.product_limit }} produtos. Você possui
      {{ storeProductStore.storeProducts.length }} produtos cadastrados.
    </v-alert>
    
    <div class="d-flex align-center mb-4">
      <v-btn color="primary" @click="openCreateDialog" :disabled="!canAddProduct">
        Adicionar Produto
      </v-btn>
      <v-btn v-if="selectedItems.length > 0" color="error" class="ml-2" @click="confirmDeleteSelected">
        Excluir Selecionados ({{ selectedItems.length }})
      </v-btn>
    </div>

    <!-- Tabela com AppDataTable - Atualizada com paginação -->
    <AppDataTable 
      :headers="filteredHeaders" 
      :items="filteredProducts"
      :loading="storeProductStore.loading"
      :search="search"
      :items-per-page="itemsPerPage"
      v-model:page="page"
      :show-select="true"
      v-model:selected="selectedItems"
      searchable
      @update:page="handlePageChange"
      @update:items-per-page="handleItemsPerPageChange"
      @update:search="search = $event"
    >
      <template v-slot:item.product.image="{ item }">
        <v-img :src="imageUrl(item.product?.image)" max-width="50" max-height="50" @error="onImageError(item)"
          @click="openImageDialog(item)" style="cursor: pointer;"></v-img>
      </template>
      <template v-slot:item.product.name="{ item }">
        {{ (item.product.name) }}
      </template>
      <template v-slot:item.product.quantity="{ item }">
        {{ formatQuantity(item.product.quantity, item.product.weight_unit) }}
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
      <template v-slot:item.actions="{ item }">
        <AppActionButtons :item="item" :show-details="false" @edit="openEditDialog"
          @delete="() => confirmDelete(item.id)" />
      </template>
    </AppDataTable>

    <!-- Diálogo para adicionar/editar produto -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          {{ isEditing ? 'Editar Produto da Loja' : 'Adicionar Produto da Loja' }}
        </v-card-title>
        <v-card-text>
          <p v-if="formData.product_id?.name">
            <strong>Nome do Produto:</strong> {{ formData.product_id.name }}
          </p>
          <v-form v-model="valid" ref="form">
            <v-autocomplete v-model="formData.product_id" :items="storeProductStore.products" item-value="id"
              item-title="name" label="Produto" :rules="[v => !!v || 'Produto é obrigatório']" required clearable
              return-object auto-select-first no-data-text="Nenhum produto disponível">
              <template v-slot:item="{ props, item }">
                <v-list-item v-bind="props" :title="null">
                  <template v-slot:prepend>
                    <v-img :src="imageUrl(item.raw.image)" width="40" height="40" class="mr-2" cover></v-img>
                  </template>
                  <v-list-item-title class="font-weight-bold">
                    {{ item.raw.name }} - {{ item.raw.quantity }}
                    {{ item.raw.weight_unit }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <span class="d-block">Peso: {{ item.raw.quantity }}
                      {{ item.raw.weight_unit }}</span>
                    <span v-if="item.raw.package_type" class="d-block">Embalagem: {{ item.raw.package_type }}</span>
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
              <template v-slot:selection="{ item }">
                <div class="d-flex align-center">
                  <v-img :src="imageUrl(item.raw.image)" width="30" height="30" class="mr-2" cover></v-img>
                  <span>{{ item.raw.name }} - {{ item.raw.quantity }}
                    {{ item.raw.weight_unit }}</span>
                </div>
              </template>
            </v-autocomplete>
            <v-text-field v-model.number="formData.price" label="Preço" type="number" step="0.01"
              :rules="[v => v > 0 || 'Preço deve ser maior que zero']" required></v-text-field>
            <template v-if="storeProfile?.use_bulk_pricing">
              <v-text-field v-model.number="formData.bulk_price" label="Preço por Quantidade" type="number" step="0.01"
                :rules="[
                  v =>
                    v === null ||
                    v >= 0 ||
                    'Preço por quantidade não pode ser negativo',
                ]"></v-text-field>
              <v-text-field v-model.number="formData.bulk_min_quantity" label="Quantidade Mínima" type="number" :rules="[
                v =>
                  v === null ||
                  v >= 0 ||
                  'Quantidade mínima não pode ser negativa',
              ]"></v-text-field>
            </template>
            <template v-if="storeProfile?.has_loyalty_card">
              <v-text-field v-model.number="formData.loyalty_price" label="Preço por Fidelidade" type="number"
                step="0.01" :rules="[
                  v =>
                    v === null ||
                    v >= 0 ||
                    'Preço por fidelidade não pode ser negativo',
                ]"></v-text-field>
            </template>
            <v-checkbox v-model="formData.is_active" label="Ativo"></v-checkbox>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveProduct" :disabled="!valid" :loading="storeProductStore.loading">
            Salvar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo para visualizar imagem e detalhes -->
    <v-dialog v-model="imageDialog" max-width="600px">
      <v-card>
        <v-card-title>Detalhes do Produto</v-card-title>
        <v-card-text>
          <v-img :src="imageUrl(selectedProduct?.product?.image)" max-height="300" contain class="mb-4"></v-img>
          <v-row>
            <v-col cols="12">
              <p>
                <strong>Nome:</strong>
                {{ selectedProduct?.product?.name || 'N/A' }}
              </p>
              <p>
                <strong>Tipo de Embalagem:</strong>
                {{ selectedProduct?.product?.package_type || 'N/A' }}
              </p>
              <p>
                <strong>Quantidade:</strong>
                {{ selectedProduct?.product?.quantity || 'N/A' }}
              </p>
              <p>
                <strong>Unidade de Peso:</strong>
                {{ selectedProduct?.product?.weight_unit || 'N/A' }}
              </p>
              <p>
                <strong>Descrição:</strong>
                {{ selectedProduct?.product?.description || 'Sem descrição' }}
              </p>
              <p><strong>Preço:</strong> {{ formatPrice(selectedProduct?.price) }}</p>
              <p v-if="storeProfile?.use_bulk_pricing">
                <strong>Preço por Quantidade:</strong>
                {{ formatPrice(selectedProduct?.bulk_price) }}
              </p>
              <p v-if="storeProfile?.use_bulk_pricing">
                <strong>Quantidade Mínima:</strong>
                {{ formatQuantity(selectedProduct?.bulk_min_quantity) }}
              </p>
              <p v-if="storeProfile?.has_loyalty_card">
                <strong>Preço por Fidelidade:</strong>
                {{ formatPrice(selectedProduct?.loyalty_price) }}
              </p>
              <p>
                <strong>Ativo:</strong>
                {{ selectedProduct?.is_active ? 'Sim' : 'Não' }}
              </p>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="imageDialog = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo de confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title>Confirmar Exclusão</v-card-title>
        <v-card-text>
          {{ selectedItems.length > 1 ?
            `Deseja realmente excluir ${selectedItems.length} produtos selecionados?` :
            selectedItems.length === 1 ?
              `Deseja realmente excluir o produto "${getProductName(selectedItems[0])}"?` :
              deleteId ? `Deseja realmente excluir o produto "${getProductName(deleteId)}"?` :
                'Deseja realmente excluir este produto?'
          }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteSelectedProducts" :loading="storeProductStore.loading">
            Excluir
          </v-btn>
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
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue';
import { useStoreProductStore } from '~/stores/storeProducts';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';
import AppDataTable from '~/components/app/AppDataTable.vue';

interface Product {
  id: number;
  name: string;
  package_type: string;
  quantity: string;
  weight_unit: string;
  description?: string;
  image?: string;
}

interface StoreProduct {
  id: number;
  product_id?: number;
  product: Product;
  price: number | string;
  bulk_price: number | null;
  bulk_min_quantity: number | null;
  loyalty_price: number | null;
  is_active: boolean;
}

const storeProductStore = useStoreProductStore();
const authStore = useAuthStore();
const router = useRouter();

// Estados
const dialog = ref(false);
const deleteDialog = ref(false);
const imageDialog = ref(false);
const isEditing = ref(false);
const valid = ref(false);
const deleteId = ref<number | null>(null);
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const selectedProduct = ref<Partial<StoreProduct> & { product?: Partial<Product> }>({});
const search = ref('');
const storeProfile = ref<any>(null);
const selectedItems = ref<number[]>([]);

// Paginação
const page = ref(1);
const itemsPerPage = ref(10);

const baseUrl = ref('http://localhost:8000');

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

const canAddProduct = computed(() => {
  if (!authStore.activePlan) return false;
  return storeProductStore.storeProducts.length < authStore.activePlan.product_limit;
});

const headers = [
  { title: 'Imagem', key: 'product.image', sortable: false },
  { title: 'Produto', key: 'product.name' },
  {
    title: 'Peso',
    key: 'product.quantity',
    value: item => `${item.product?.quantity} ${item.product?.weight_unit}`,
  },
  { title: 'Preço', key: 'price' },
  { title: 'Preço por Quantidade', key: 'bulk_price' },
  { title: 'Quantidade Mínima', key: 'bulk_min_quantity' },
  { title: 'Preço por Fidelidade', key: 'loyalty_price' },
  { title: 'Ativo', key: 'is_active' },
  { title: 'Ações', key: 'actions', sortable: false },
];

const filteredHeaders = computed(() => {
  return headers.filter(header => {
    if (header.key === 'bulk_price' || header.key === 'bulk_min_quantity') {
      return storeProfile.value?.use_bulk_pricing;
    }
    if (header.key === 'loyalty_price') {
      return storeProfile.value?.has_loyalty_card;
    }
    return true;
  });
});

// Produtos filtrados
const filteredProducts = computed(() => {
  if (!search.value) return storeProductStore.storeProducts;
  
  const searchTerm = search.value.toLowerCase();
  return storeProductStore.storeProducts.filter(product => {
    const priceStr = product.price ? formatPrice(product.price).toLowerCase() : '';
    const bulkPriceStr = product.bulk_price ? formatPrice(product.bulk_price).toLowerCase() : '';
    const loyaltyPriceStr = product.loyalty_price ? formatPrice(product.loyalty_price).toLowerCase() : '';
    const quantityStr = product.product?.quantity ? 
      `${product.product.quantity}${product.product.weight_unit || ''}`.toLowerCase() : '';
    
    return (
      (product.product?.name?.toLowerCase().includes(searchTerm)) ||
      (product.product?.package_type?.toLowerCase().includes(searchTerm)) ||
      (product.product?.description?.toLowerCase().includes(searchTerm)) ||
      (priceStr.includes(searchTerm)) ||
      (bulkPriceStr.includes(searchTerm)) ||
      (loyaltyPriceStr.includes(searchTerm)) ||
      (quantityStr.includes(searchTerm))
    );
  });
});

// Calcula total de páginas
const totalPages = computed(() => {
  if (itemsPerPage.value === -1) return 1;
  return Math.ceil(filteredProducts.value.length / itemsPerPage.value);
});

// Manipuladores de paginação
const handlePageChange = (newPage: number) => {
  page.value = newPage;
};

const handleItemsPerPageChange = (newItemsPerPage: number) => {
  itemsPerPage.value = newItemsPerPage;
  page.value = 1; // Resetar para a primeira página
};

const formData = reactive({
  id: null as number | null,
  product_id: null as number | null | { id: number },
  price: 0,
  bulk_price: null as number | null,
  bulk_min_quantity: null as number | null,
  loyalty_price: null as number | null,
  is_active: true,
});

onMounted(async () => {
  if (authStore.isStore) {
    await authStore.fetchProfile();
    storeProfile.value = authStore.user;
  } else {
    router.push('/');
  }
  await storeProductStore.fetchStoreProducts();
  await storeProductStore.fetchProducts();
});

function getProductName(id: number) {
  const product = storeProductStore.storeProducts.find(p => p.id === id);
  return product?.product?.name || 'Produto desconhecido';
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

function onImageError(item: any) {
  console.error(
    `Erro ao carregar imagem para o produto ${item.product?.name}: ${item.product?.image}`
  );
}

function openImageDialog(item: StoreProduct) {
  selectedProduct.value = { ...item };
  imageDialog.value = true;
}

function openCreateDialog() {
  if (!canAddProduct.value) {
    snackbarText.value =
      'Limite de produtos do plano atingido. Atualize seu plano para adicionar mais produtos.';
    snackbarColor.value = 'error';
    snackbar.value = true;
    return;
  }
  isEditing.value = false;
  Object.assign(formData, {
    id: null,
    product_id: null,
    price: 0,
    bulk_price: storeProfile.value?.use_bulk_pricing ? null : null,
    bulk_min_quantity: storeProfile.value?.use_bulk_pricing ? null : null,
    loyalty_price: storeProfile.value?.has_loyalty_card ? null : null,
    is_active: true,
  });
  dialog.value = true;
}

async function openEditDialog(item: StoreProduct) {
  isEditing.value = true;

  if (!storeProductStore.products.length) {
    await storeProductStore.fetchProducts();
  }

  let selectedProduct: Product | undefined;
  const productId = item.product_id ?? item.product?.id;
  if (productId) {
    selectedProduct = storeProductStore.products.find(
      (product: Product) => product.id === productId
    );
  }

  Object.assign(formData, {
    id: item.id,
    product_id: selectedProduct || null,
    price: typeof item.price === 'string' ? parseFloat(item.price) : item.price,
    bulk_price: storeProfile.value?.use_bulk_pricing ? item.bulk_price : null,
    bulk_min_quantity: storeProfile.value?.use_bulk_pricing ? item.bulk_min_quantity : null,
    loyalty_price: storeProfile.value?.has_loyalty_card ? item.loyalty_price : null,
    is_active: item.is_active,
  });
  dialog.value = true;
}

async function saveProduct() {
  if (!valid.value) return;

  const productId = typeof formData.product_id === 'object' && formData.product_id
    ? formData.product_id.id
    : formData.product_id;

  if (!productId) {
    snackbarText.value = 'Nenhum produto selecionado.';
    snackbarColor.value = 'error';
    snackbar.value = true;
    return;
  }

  await storeProductStore.fetchStoreProducts();

  // Verificar duplicatas
  const existingProduct = storeProductStore.storeProducts.find((p) => {
    const existingProductId = p.product_id ?? p.product?.id;
    return existingProductId === productId && (!isEditing.value || p.id !== formData.id);
  });

  if (existingProduct) {
    snackbarText.value = 'Este produto já está cadastrado na loja.';
    snackbarColor.value = 'error';
    snackbar.value = true;
    return;
  }

  const data = {
    product_id: productId,
    price: formData.price,
    bulk_price: storeProfile.value?.use_bulk_pricing ? formData.bulk_price : null,
    bulk_min_quantity: storeProfile.value?.use_bulk_pricing ? formData.bulk_min_quantity : null,
    loyalty_price: storeProfile.value?.has_loyalty_card ? formData.loyalty_price : null,
    is_active: formData.is_active,
  };

  try {
    if (isEditing.value && formData.id) {
      await storeProductStore.updateStoreProduct(formData.id, data);
      snackbarText.value = 'Produto atualizado com sucesso!';
      snackbarColor.value = 'success';
    } else {
      await storeProductStore.createStoreProduct(data);
      snackbarText.value = 'Produto criado com sucesso!';
      snackbarColor.value = 'success';
    }
    dialog.value = false;
  } catch (err) {
    snackbarText.value =
      storeProductStore.error || 'Erro ao salvar produto da loja';
    snackbarColor.value = 'error';
    console.error('Erro ao salvar produto:', err);
  }
  snackbar.value = true;
}

function confirmDelete(id: number) {
  deleteId.value = id;
  selectedItems.value = [];
  deleteDialog.value = true;
}

function confirmDeleteSelected() {
  deleteId.value = null;
  deleteDialog.value = true;
}

async function deleteSelectedProducts() {
  try {
    if (deleteId.value) {
      await storeProductStore.deleteStoreProduct(deleteId.value);
      snackbarText.value = 'Produto excluído com sucesso!';
    } else if (selectedItems.value.length > 0) {
      const validItems = selectedItems.value
        .map(id => storeProductStore.storeProducts.find(product => product.id === id))
        .filter(item => item && item.id !== undefined && item.id !== null);
      if (validItems.length === 0) {
        throw new Error('Nenhum item válido selecionado para exclusão');
      }
      await Promise.all(validItems.map(item => storeProductStore.deleteStoreProduct(item.id)));
      snackbarText.value = `${validItems.length} produtos excluídos com sucesso!`;
      selectedItems.value = [];
    } else {
      throw new Error('Nenhum produto selecionado para exclusão');
    }
    snackbarColor.value = 'success';
    await storeProductStore.fetchStoreProducts();
    page.value = 1;
  } catch (err) {
    console.error('Erro ao excluir produto(s):', err);
    snackbarText.value = storeProductStore.error || `Erro ao excluir produto(s): ${err.message}`;
    snackbarColor.value = 'error';
  }
  snackbar.value = true;
  deleteDialog.value = false;
  deleteId.value = null;
}
</script>

<style scoped>
.no-border {
  border: none !important;
  box-shadow: none !important;
}

.v-list-item__title {
  white-space: normal !important;
}

.v-data-table {
  border-radius: 0;
  border: none;
}

.v-pagination {
  justify-content: center;
}

.v-chip {
  font-weight: 500;
}

.v-btn {
  text-transform: none;
}
</style>