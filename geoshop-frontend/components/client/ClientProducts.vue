<!-- pages/client/index.vue -->
<template>
  <v-container fluid class="pa-6">
    <h2 class="text-h4 font-weight-bold text-primary mb-6">Minhas Listas de Compras</h2>

    <!-- Formulário para criar nova lista -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>Criar Nova Lista</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="createCart">
          <v-text-field
            v-model="newCartName"
            label="Nome da Lista"
            prepend-inner-icon="mdi-cart"
            outlined
            :rules="[v => !!v || 'Nome da lista é obrigatório']"
          />
          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            :disabled="!newCartName"
          >
            Criar Lista
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Tabela de listas -->
    <AppDataTable
      :headers="cartHeaders"
      :items="authStore.carts"
      :loading="loading"
      searchable
      show-select
      v-model:selected="selectedCarts"
    >
      <template #item.items="{ item }">
        {{ item.items.length }} itens
      </template>
      <template #item.total_price="{ item }">
        R$ {{ item.total_price.toFixed(2) }}
      </template>
      <template #item.actions="{ item }">
        <AppActionButtons
          :item="item"
          show-details
          show-edit
          show-delete
          @details="openCartDetails(item)"
          @edit="openEditCart(item)"
          @delete="confirmDeleteCart(item)"
        >
          <v-btn
            icon
            color="primary"
            @click="findBestStore(item)"
            :loading="bestStoreLoading && selectedCartId === item.id"
          >
            <v-icon>mdi-store-search</v-icon>
          </v-btn>
        </AppActionButtons>
      </template>
    </AppDataTable>

    <!-- Modal de detalhes da lista -->
    <v-dialog v-model="cartDetailsModal" max-width="800" persistent>
      <v-card>
        <v-card-title class="text-h5 font-weight-bold text-primary">
          Detalhes da Lista: {{ selectedCart?.name }}
        </v-card-title>
        <v-card-text>
          <ProductSelector
            v-if="selectedCart"
            :cart-id="selectedCart.id"
            @item-added="fetchCarts"
            @item-updated="fetchCarts"
            @item-deleted="fetchCarts"
          />
          <v-data-table
            :headers="cartItemHeaders"
            :items="selectedCart?.items || []"
            :loading="loading"
          >
            <template #item.quantity="{ item }">
              <v-text-field
                v-model.number="item.quantity"
                type="number"
                min="1"
                dense
                style="width: 100px"
                @change="updateCartItem(item.id, { quantity: item.quantity })"
              />
            </template>
            <template #item.selected_price="{ item }">
              R$ {{ item.selected_price.toFixed(2) }}
            </template>
            <template #item.actions="{ item }">
              <v-btn
                icon
                color="error"
                @click="deleteCartItem(item.id)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" @click="cartDetailsModal = false">Fechar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal de edição da lista -->
    <v-dialog v-model="editCartModal" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5 font-weight-bold text-primary">
          Editar Lista
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="updateCart">
            <v-text-field
              v-model="editCartForm.name"
              label="Nome da Lista"
              prepend-inner-icon="mdi-cart"
              outlined
              :rules="[v => !!v || 'Nome da lista é obrigatório']"
            />
            <v-btn
              type="submit"
              color="primary"
              :loading="loading"
              :disabled="!editCartForm.name"
            >
              Salvar
            </v-btn>
            <v-btn color="grey" @click="editCartModal = false" class="ml-2">
              Cancelar
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Modal de confirmação de exclusão -->
    <v-dialog v-model="confirmDeleteCartModal" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5 font-weight-bold text-primary">
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir a lista "{{ selectedCart?.name }}"?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" @click="confirmDeleteCartModal = false">Cancelar</v-btn>
          <v-btn
            color="error"
            @click="deleteCart"
            :loading="loading"
          >
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal de melhor loja -->
    <v-dialog v-model="bestStoreModal" max-width="600" persistent>
      <BestStoreResult
        :best-store="bestStore"
        @close="bestStoreModal = false"
      />
    </v-dialog>

    <v-alert 
      v-if="error"
      :type="error.includes('sucesso') ? 'success' : 'error'"
      variant="tonal"
      class="mt-4"
      dismissible
    >
      {{ error }}
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '~/stores/auth';
import AppDataTable from '~/components/app/AppDataTable.vue';
import AppActionButtons from '~/components/app/AppActionButtons.vue';
import ProductSelector from '~/components/client/ProductSelector.vue';
import BestStoreResult from '~/components/client/BestStoreResult.vue';

definePageMeta({
  layout: 'default',
});

const authStore = useAuthStore();
const newCartName = ref('');
const loading = ref(false);
const error = ref('');
const cartDetailsModal = ref(false);
const editCartModal = ref(false);
const confirmDeleteCartModal = ref(false);
const bestStoreModal = ref(false);
const selectedCart = ref<Cart | null>(null);
const selectedCartId = ref<number | null>(null);
const bestStoreLoading = ref(false);
const bestStore = ref<any>(null);
const selectedCarts = ref<Cart[]>([]);

const cartHeaders = ref([
  { title: 'Nome', key: 'name' },
  { title: 'Itens', key: 'items' },
  { title: 'Preço Total', key: 'total_price' },
  { title: 'Criado em', key: 'created_at' },
  { title: 'Ações', key: 'actions', sortable: false },
]);

const cartItemHeaders = ref([
  { title: 'Produto', key: 'product.name' },
  { title: 'Quantidade', key: 'quantity' },
  { title: 'Preço Unitário', key: 'selected_price' },
  { title: 'Ações', key: 'actions', sortable: false },
]);

onMounted(async () => {
  if (!authStore.isClient) {
    await navigateTo('/');
    return;
  }
  await fetchCarts();
});

async function fetchCarts() {
  try {
    loading.value = true;
    await authStore.fetchCarts();
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar listas';
  } finally {
    loading.value = false;
  }
}

async function createCart() {
  try {
    loading.value = true;
    error.value = '';
    await authStore.createCart(newCartName.value);
    newCartName.value = '';
    error.value = 'Lista criada com sucesso!';
  } catch (err: any) {
    error.value = err.message || 'Erro ao criar lista';
  } finally {
    loading.value = false;
  }
}

function openCartDetails(cart: Cart) {
  selectedCart.value = cart;
  cartDetailsModal.value = true;
}

function openEditCart(cart: Cart) {
  selectedCart.value = cart;
  editCartForm.value = { name: cart.name };
  editCartModal.value = true;
}

function confirmDeleteCart(cart: Cart) {
  selectedCart.value = cart;
  confirmDeleteCartModal.value = true;
}

async function updateCart() {
  if (!selectedCart.value) return;
  try {
    loading.value = true;
    error.value = '';
    await authStore.updateCart(selectedCart.value.id, { name: editCartForm.value.name });
    error.value = 'Lista atualizada com sucesso!';
    editCartModal.value = false;
  } catch (err: any) {
    error.value = err.message || 'Erro ao atualizar lista';
  } finally {
    loading.value = false;
  }
}

async function deleteCart() {
  if (!selectedCart.value) return;
  try {
    loading.value = true;
    error.value = '';
    await authStore.deleteCart(selectedCart.value.id);
    error.value = 'Lista excluída com sucesso!';
    confirmDeleteCartModal.value = false;
    selectedCart.value = null;
  } catch (err: any) {
    error.value = err.message || 'Erro ao excluir lista';
  } finally {
    loading.value = false;
  }
}

async function updateCartItem(cartItemId: number, data: { quantity: number }) {
  try {
    loading.value = true;
    error.value = '';
    await authStore.updateCartItem(cartItemId, data);
    error.value = 'Item atualizado com sucesso!';
  } catch (err: any) {
    error.value = err.message || 'Erro ao atualizar item';
  } finally {
    loading.value = false;
  }
}

async function deleteCartItem(cartItemId: number) {
  try {
    loading.value = true;
    error.value = '';
    await authStore.deleteCartItem(cartItemId);
    error.value = 'Item removido com sucesso!';
  } catch (err: any) {
    error.value = err.message || 'Erro ao remover item';
  } finally {
    loading.value = false;
  }
}

async function findBestStore(cart: Cart) {
  try {
    bestStoreLoading.value = true;
    selectedCartId.value = cart.id;
    error.value = '';
    bestStore.value = await authStore.getBestStore(cart.id);
    bestStoreModal.value = true;
  } catch (err: any) {
    error.value = err.message || 'Nenhuma loja encontrada para esta lista';
  } finally {
    bestStoreLoading.value = false;
  }
}

const editCartForm = ref({ name: '' });
</script>

<style scoped>
.v-btn {
  text-transform: none;
  letter-spacing: normal;
}
</style>