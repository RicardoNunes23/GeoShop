import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';

export const useProductStore = defineStore('product', () => {
  const storeProducts = ref<StoreProduct[]>([]);
  const products = ref<Product[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const { public: { apiBase } } = useRuntimeConfig();

  // Interface para Product
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

  // Interface para StoreProduct
  interface StoreProduct {
    id: number;
    store: number;
    product: Product;
    price: number;
    bulk_price: number | null;
    bulk_min_quantity: number | null;
    loyalty_price: number | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }

  // Função para buscar todos os produtos
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

  // Função para criar um produto
  async function createProduct(productData: FormData): Promise<Product> {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/products/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      });
      return response as Product;
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao criar produto';
      console.error('Erro ao criar produto:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Função para atualizar um produto
  async function updateProduct(id: number, productData: FormData) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      const response = await $fetch(`${apiBase}/products/${id}/`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      });
      const index = products.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        products.value[index] = response as Product;
      }
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao atualizar produto';
      console.error('Erro ao atualizar produto:', err);
    } finally {
      loading.value = false;
    }
  }

  // Função para excluir um produto
  async function deleteProduct(id: number) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      await $fetch(`${apiBase}/products/${id}/`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      products.value = products.value.filter((p) => p.id !== id);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao excluir produto';
      console.error('Erro ao excluir produto:', err);
    } finally {
      loading.value = false;
    }
  }

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

  // Função para excluir um produto da loja
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

  return {
    storeProducts,
    products,
    loading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    fetchStoreProducts,
    createStoreProduct,
    updateStoreProduct,
    deleteStoreProduct,
  };
});