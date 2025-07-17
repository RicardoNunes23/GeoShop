// stores/productStore.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth' // Supondo que você tenha uma store de autenticação

interface Product {
  id: number
  name: string
  brand: string
  package_type: string
  quantity: number
  weight_unit: string
  description?: string
  image?: string
  admin: number
  created_at: string
  updated_at: string
}

export const useProductStore = defineStore('product', () => {
  const products = ref<Product[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const { public: { apiBase } } = useRuntimeConfig() // Obtém a URL base do nuxt.config.ts

  // Função para buscar todos os produtos
  async function fetchProducts() {
    loading.value = true
    error.value = null
    try {
      const authStore = useAuthStore()
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado')
      }
      const response = await $fetch(`${apiBase}/products/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      })
      products.value = response as Product[]
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar produtos'
      console.error('Erro ao buscar produtos:', err)
    } finally {
      loading.value = false
    }
  }

  // Função para criar um produto
  async function createProduct(productData: FormData) {
    loading.value = true
    error.value = null
    try {
      const authStore = useAuthStore()
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado')
      }
      const response = await $fetch(`${apiBase}/products/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      })
      products.value.push(response as Product)
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao criar produto'
      console.error('Erro ao criar produto:', err)
    } finally {
      loading.value = false
    }
  }

  // Função para atualizar um produto
  async function updateProduct(id: number, productData: FormData) {
    loading.value = true
    error.value = null
    try {
      const authStore = useAuthStore()
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado')
      }
      const response = await $fetch(`${apiBase}/products/${id}/`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: productData,
      })
      const index = products.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        products.value[index] = response as Product
      }
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao atualizar produto'
      console.error('Erro ao atualizar produto:', err)
    } finally {
      loading.value = false
    }
  }

  // Função para excluir um produto
 async function deleteProduct(id: number) {
  loading.value = true
  error.value = null
  try {
    const authStore = useAuthStore()
    if (!authStore.token) {
      throw new Error('Token de autenticação não encontrado')
    }
    await $fetch(`${apiBase}/products/${id}/`, { 
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
    })
    products.value = products.value.filter((p) => p.id !== id)
  } catch (err: any) {
    error.value = err.data?.detail || 'Erro ao excluir produto'
    console.error('Erro ao excluir produto:', err)
  } finally {
    loading.value = false
  }
}

  return { products, loading, error, fetchProducts, createProduct, updateProduct, deleteProduct }
})