<!-- components/app/ProductSelector.vue -->
<template>
  <v-container fluid class="pa-0">
    <v-form @submit.prevent="addItem">
      <v-row align="center">
        <v-col cols="12" md="5">
          <v-autocomplete
            v-model="selectedProduct"
            :items="products"
            item-title="name"
            item-value="id"
            label="Selecionar Produto"
            prepend-inner-icon="mdi-cart"
            outlined
            :rules="[v => !!v || 'Produto é obrigatório']"
          />
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field
            v-model.number="quantity"
            label="Quantidade"
            type="number"
            min="1"
            outlined
            :rules="[v => v > 0 || 'Quantidade deve ser maior que 0']"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-btn
            type="submit"
            color="primary"
            :loading="loading"
            :disabled="!selectedProduct || !quantity"
          >
            Adicionar Item
          </v-btn>
        </v-col>
      </v-row>
    </v-form>

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      class="mt-4"
      dismissible
    >
      {{ error }}
    </v-alert>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '~/stores/auth';

const props = defineProps({
  cartId: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(['item-added', 'item-updated', 'item-deleted']);

const authStore = useAuthStore();
const products = ref([]);
const selectedProduct = ref<number | null>(null);
const quantity = ref(1);
const loading = ref(false);
const error = ref('');

onMounted(async () => {
  await fetchProducts();
});

async function fetchProducts() {
  try {
    loading.value = true;
    const response = await axios.get(`${useRuntimeConfig().public.apiBase}/products/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    });
    products.value = response.data;
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar produtos';
  } finally {
    loading.value = false;
  }
}

async function addItem() {
  if (!selectedProduct.value) return;
  try {
    loading.value = true;
    error.value = '';
    await authStore.addCartItem(props.cartId, selectedProduct.value, quantity.value);
    emit('item-added');
    selectedProduct.value = null;
    quantity.value = 1;
  } catch (err: any) {
    error.value = err.message || 'Erro ao adicionar item';
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.v-btn {
  text-transform: none;
  letter-spacing: normal;
}
</style>