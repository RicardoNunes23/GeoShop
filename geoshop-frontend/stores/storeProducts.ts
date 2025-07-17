import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth'; // Supondo que você tenha uma store de autenticação


export const useStoreProductStore = defineStore('storeProduct', () => {
  const storeProducts = ref<StoreProduct[]>([]);
  const products = ref<Product[]>([]); // Para o select de produtos
  const loading = ref(false);
  const error = ref<string | null>(null);
  const { public: { apiBase } } = useRuntimeConfig();

  // Função para buscar todos os produtos da loja
  async function fetchStoreProducts() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/store-products/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      storeProducts.value = response as StoreProduct[];
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar produtos da loja';
      console.error('Erro ao buscar produtos da loja:', err);
    } finally {
      loading.value = false;
    }
  }

  // Função para buscar produtos disponíveis (para o select)
  async function fetchProducts() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/products/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      products.value = response as Product[];
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar produtos';
      console.error('Erro ao buscar produtos:', err);
    } finally {
      loading.value = false;
    }
  }

  // Função para criar um produto da loja
  async function createStoreProduct(productData: FormData) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/store-products/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      });
      storeProducts.value.push(response as StoreProduct);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao criar produto da loja';
      console.error('Erro ao criar produto da loja:', err);
    } finally {
      loading.value = false;
    }
  }

  // Função para atualizar um produto da loja
  async function updateStoreProduct(id: number, productData: FormData) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/store-products/${id}/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      });
      const index = storeProducts.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        storeProducts.value[index] = response as StoreProduct;
      }
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao atualizar produto da loja';
      console.error('Erro ao atualizar produto da loja:', err);
    } finally {
      loading.value = false;
    }
  }

  // Função para excluir umრ

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
    } finally {
      loading.value = false;
    }
  }

  return { storeProducts, products, loading, error, fetchStoreProducts, fetchProducts, createStoreProduct, updateStoreProduct, deleteStoreProduct };
});