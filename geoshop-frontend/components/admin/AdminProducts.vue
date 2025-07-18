<!-- pages/products.vue -->
<template>
  <v-container>
    <h1>Gerenciamento de Produtos</h1>
    <div class="d-flex align-center mb-4">
      <v-btn color="primary" @click="openCreateDialog">Adicionar Produto</v-btn>
      <v-btn
        v-if="selectedItems.length > 0"
        color="error"
        class="ml-2"
        @click="confirmDeleteSelected"
      >
        Excluir Selecionados ({{ selectedItems.length }})
      </v-btn>
    </div>

    <AppDataTable
      :headers="headers"
      :items="filteredProducts"
      :loading="productStore.loading"
      :show-select="true"
      v-model:selected="selectedItems"
      searchable
    >
      <template v-slot:item.image="{ item }">
        <v-img
          :src="imageUrl(item.image)"
          max-width="50"
          max-height="50"
          @error="onImageError(item)"
          @click="openImageDialog(item)"
          style="cursor: pointer;"
        ></v-img>
      </template>
      <template v-slot:actions="{ item }">
        <v-btn color="warning" small @click="openEditDialog(item)">Editar</v-btn>
        <v-btn color="error" small @click="confirmDelete(item.id)">Excluir</v-btn>
      </template>
    </AppDataTable>

    <!-- Diálogo para adicionar/editar produto -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          {{ isEditing ? 'Editar Produto' : 'Adicionar Produto' }}
        </v-card-title>
        <v-card-text>
          <v-form v-model="valid" ref="form">
            <v-text-field
              v-model="formData.name"
              label="Produto/ Marca"
              :rules="[v => !!v || 'Nome é obrigatório']"
              required
            ></v-text-field>
            <v-select
              v-model="formData.package_type"
              :items="packageTypes"
              item-value="value"
              item-title="text"
              label="Tipo de Embalagem"
              :rules="[v => !!v || 'Tipo de embalagem é obrigatório']"
              required
            ></v-select>
            <v-text-field
              v-model="combinedQuantity"
              label="Quantidade (ex: 5kg, 100g, 1L, 2un)"
              :rules="[validateCombinedQuantity]"
              required
              @blur="parseCombinedQuantity"
            ></v-text-field>
            <v-textarea
              v-model="formData.description"
              label="Descrição"
              rows="3"
            ></v-textarea>
            <v-file-input
              v-model="formData.image"
              label="Imagem do Produto"
              accept="image/*"
            ></v-file-input>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="dialog = false">Cancelar</v-btn>
          <v-btn color="primary" @click="saveProduct" :disabled="!valid">Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Diálogo para visualizar imagem e detalhes -->
    <v-dialog v-model="imageDialog" max-width="600px">
      <v-card>
        <v-card-title>Detalhes do Produto</v-card-title>
        <v-card-text>
          <v-img
            :src="imageUrl(selectedProduct.image)"
            max-height="300"
            contain
            class="mb-4"
          ></v-img>
          <v-row>
            <v-col cols="12">
              <p><strong>Produto/ Marca:</strong> {{ selectedProduct.name }}</p>
              <p><strong>Tipo de Embalagem:</strong> {{ selectedProduct.package_type }}</p>
              <p><strong>Quantidade:</strong> {{ formatQuantity(selectedProduct.quantity, selectedProduct.weight_unit) }}</p>
              <p><strong>Descrição:</strong> {{ selectedProduct.description || 'Sem descrição' }}</p>
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
          {{ selectedItems.length > 0 ? 
            `Deseja realmente excluir ${selectedItems.length} produtos selecionados?` : 
            'Deseja realmente excluir este produto?' 
          }}
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteSelectedProducts">Excluir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="snackbar = false">Fechar</v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useProductStore } from '~/stores/products';
import AppDataTable from '~/components/AppDataTable.vue';

definePageMeta({
  middleware: ['auth'],
});

const productStore = useProductStore();
const dialog = ref(false);
const deleteDialog = ref(false);
const imageDialog = ref(false);
const isEditing = ref(false);
const valid = ref(false);
const deleteId = ref<number | null>(null);
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const selectedProduct = ref<any>({});
const search = ref('');
const selectedItems = ref<number[]>([]);
const combinedQuantity = ref('');

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

const formData = ref({
  id: null as number | null,
  name: '',
  package_type: '',
  quantity: 0,
  weight_unit: '',
  description: '',
  image: null as File | null,
});

const packageTypes = [
  { text: 'Saco', value: 'saco' },
  { text: 'Pacote', value: 'pacote' },
  { text: 'Lata', value: 'lata' },
  { text: 'Caixa', value: 'caixa' },
  { text: 'Bandeja', value: 'bandeja' },
  { text: 'Garrafa', value: 'garrafa' },
  { text: 'Outro', value: 'outro' },
];

const unitOptions = [
  { text: 'kg', value: 'kg' },
  { text: 'g', value: 'g' },
  { text: 'ml', value: 'ml' },
  { text: 'L', value: 'l' },
  { text: 'un', value: 'un' },
];

const headers = [
  { title: 'Imagem', key: 'image', sortable: false },
  { title: 'Produto/ Marca', key: 'name' },
  {
    title: 'Tipo de Embalagem',
    key: 'package_type',
    value: (item) => item.package_type ? item.package_type.charAt(0).toUpperCase() + item.package_type.slice(1) : '',
  },
  {
    title: 'Quantidade',
    key: 'quantity',
    value: (item) => formatQuantity(item.quantity, item.weight_unit),
  },
  { title: 'Ações', key: 'actions', sortable: false },
];

const filteredProducts = computed(() => {
  if (!search.value) return productStore.products;

  const searchTerm = search.value.toLowerCase();
  return productStore.products.filter(product => {
    const quantityStr = product.quantity ? `${product.quantity}${product.weight_unit}`.toLowerCase() : '';
    return (
      (product.name?.toLowerCase().includes(searchTerm)) ||
      (product.package_type?.toLowerCase().includes(searchTerm)) ||
      (product.description?.toLowerCase().includes(searchTerm)) ||
      (quantityStr.includes(searchTerm))
    );
  });
});

onMounted(() => {
  productStore.fetchProducts().then(() => {
    console.log('Produtos carregados:', productStore.products);
  });
});

function formatQuantity(quantity: number, unit: string) {
  const formattedValue = Number.isInteger(quantity) 
    ? quantity.toString() 
    : parseFloat(quantity.toString()).toString();
  const formattedUnit = unit.toLowerCase() === 'l' ? 'L' : unit.toLowerCase();
  return `${formattedValue}${formattedUnit}`;
}

function onImageError(item: any) {
  console.error(`Erro ao carregar imagem para o produto ${item.name}: ${item.image}`);
}

function openImageDialog(item: any) {
  selectedProduct.value = { ...item };
  imageDialog.value = true;
}

function openCreateDialog() {
  isEditing.value = false;
  formData.value = {
    id: null,
    name: '',
    package_type: '',
    quantity: 0,
    weight_unit: '',
    description: '',
    image: null,
  };
  combinedQuantity.value = '';
  dialog.value = true;
}

function openEditDialog(item: any) {
  isEditing.value = true;
  formData.value = {
    id: item.id,
    name: item.name || '',
    package_type: typeof item.package_type === 'string' ? item.package_type : '',
    quantity: item.quantity || 0,
    weight_unit: typeof item.weight_unit === 'string' ? item.weight_unit : '',
    description: item.description || '',
    image: null,
  };
  combinedQuantity.value = `${item.quantity}${item.weight_unit}`;
  dialog.value = true;
}

const validateCombinedQuantity = (value: string) => {
  if (!value) return 'Quantidade é obrigatória';
  const hasValidUnit = unitOptions.some(unit => value.toLowerCase().endsWith(unit.value));
  if (!hasValidUnit) {
    return 'Formato inválido. Use: número + unidade (ex: 5kg, 100g, 1L, 2un)';
  }
  const numericValue = parseCombinedValue(value);
  if (isNaN(numericValue)) {
    return 'Quantidade deve ser um número válido';
  }
  if (numericValue <= 0) {
    return 'Quantidade deve ser maior que zero';
  }
  return true;
};

function parseCombinedValue(value: string): number {
  const sortedUnits = [...unitOptions].sort((a, b) => b.value.length - a.value.length);
  const matchedUnit = sortedUnits.find(unit => value.toLowerCase().endsWith(unit.value));
  if (matchedUnit) {
    const numericPart = value.substring(0, value.length - matchedUnit.value.length);
    return parseFloat(numericPart);
  }
  return NaN;
}

function parseCombinedQuantity() {
  if (!combinedQuantity.value) return;
  const matchedUnit = unitOptions.find(unit => combinedQuantity.value.toLowerCase().endsWith(unit.value));
  if (matchedUnit) {
    const numericValue = parseCombinedValue(combinedQuantity.value);
    if (!isNaN(numericValue)) {
      formData.value.quantity = numericValue;
      formData.value.weight_unit = matchedUnit.value;
    }
  }
}

async function saveProduct() {
  parseCombinedQuantity();
  const data = new FormData();
  data.append('name', formData.value.name);
  data.append('package_type', formData.value.package_type);
  data.append('quantity', String(formData.value.quantity));
  data.append('weight_unit', formData.value.weight_unit);
  if (formData.value.description) data.append('description', formData.value.description);
  if (formData.value.image) {
    data.append('image', formData.value.image);
  }

  try {
    if (isEditing.value && formData.value.id) {
      await productStore.updateProduct(formData.value.id, data);
      snackbarText.value = 'Produto atualizado com sucesso!';
      snackbarColor.value = 'success';
    } else {
      await productStore.createProduct(data);
      snackbarText.value = 'Produto criado com sucesso!';
      snackbarColor.value = 'success';
    }
    dialog.value = false;
  } catch (err) {
    snackbarText.value = productStore.error || 'Erro ao salvar produto';
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
      await productStore.deleteProduct(deleteId.value);
      snackbarText.value = 'Produto excluído com sucesso!';
    } else if (selectedItems.value.length > 0) {
      const validItems = selectedItems.value
        .map(id => productStore.products.find(product => product.id === id))
        .filter(item => item && item.id !== undefined && item.id !== null);
      if (validItems.length === 0) {
        throw new Error('Nenhum item válido selecionado para exclusão');
      }
      await Promise.all(validItems.map(item => productStore.deleteProduct(item.id)));
      snackbarText.value = `${validItems.length} produtos excluídos com sucesso!`;
      selectedItems.value = [];
    } else {
      throw new Error('Nenhum produto selecionado para exclusão');
    }
    snackbarColor.value = 'success';
  } catch (err) {
    console.error('Erro ao excluir produto(s):', err);
    snackbarText.value = productStore.error || `Erro ao excluir produto(s): ${err.message}`;
    snackbarColor.value = 'error';
  }
  snackbar.value = true;
  deleteDialog.value = false;
  deleteId.value = null;
}
</script>