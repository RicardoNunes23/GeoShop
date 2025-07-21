import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';

export interface Product {
  id: number;
  name: string;
  package_type: string;
  quantity: string;
  weight_unit: string;
  description?: string;
  image?: string;
}

export interface StoreProduct {
  id: number;
  product_id?: number;
  product: Product;
  price: number | string;
  bulk_price: number | null;
  bulk_min_quantity: number | null;
  loyalty_price: number | null;
  is_active: boolean;
}

export const useStoreProductStore = defineStore('storeProduct', () => {
  const storeProducts = ref<StoreProduct[]>([]);
  const products = ref<Product[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const { public: { apiBase } } = useRuntimeConfig();

  async function fetchStoreProducts() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch<StoreProduct[]>(`${apiBase}/store-products/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      storeProducts.value = response;
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar produtos da loja';
      console.error('Erro ao buscar produtos da loja:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchProducts() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch<Product[]>(`${apiBase}/products/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      products.value = response;
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar produtos';
      console.error('Erro ao buscar produtos:', err);
    } finally {
      loading.value = false;
    }
  }

  async function createStoreProduct(productData: Partial<StoreProduct>) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      console.log('Enviando dados para criação:', productData);
      const response = await $fetch<StoreProduct>(`${apiBase}/store-products/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData),
      });
      storeProducts.value.push(response);
      console.log('Produto criado com sucesso:', response);
    } catch (err: any) {
      error.value = err.data?.detail || err.message || 'Erro ao criar produto da loja';
      console.error('Erro ao criar produto da loja:', err, 'Resposta:', err.response);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateStoreProduct(id: number, productData: Partial<StoreProduct>) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      console.log('Enviando dados para atualização:', { id, productData });
      const response = await $fetch<StoreProduct>(`${apiBase}/store-products/${id}/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData),
      });
      const index = storeProducts.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        storeProducts.value[index] = response;
      }
    } catch (err: any) {
      error.value = err.data?.detail || err.message || 'Erro ao atualizar produto da loja';
      console.error('Erro ao atualizar produto da loja:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteStoreProduct(id: number) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      await $fetch(`${apiBase}/store-products/${id}/`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      storeProducts.value = storeProducts.value.filter((p) => p.id !== id);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao excluir produto da loja';
      console.error('Erro ao excluir produto da loja:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return { storeProducts, products, loading, error, fetchStoreProducts, fetchProducts, createStoreProduct, updateStoreProduct, deleteStoreProduct };
});