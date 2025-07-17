<template>
  <div class="admin-container">
 
    <p v-if="!authStore.isAdmin" class="error-message">
      Acesso restrito a administradores
    </p>
    
    <div v-else>
      <!-- Componente dinâmico com base no parâmetro 'view' -->
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth';
import { useRoute, useRouter } from '#app';
import { computed } from 'vue';

// Importe os componentes que serão usados
import UserProfile from '~/components/admin/UserProfile.vue';
import AdminProducts from '~/components/admin/AdminProducts.vue';
import AdminStoreProducts from '~/components/admin/AdminStoreProducts.vue';
import AdminPlans from '~/components/admin/AdminPlans.vue';
//import Orders from '~/components/admin/Orders.vue';
//import Settings from '~/components/admin/Settings.vue';

definePageMeta({
  middleware: ['auth'],
  layout: 'sidebar'
});

// Estado do layout
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

// Define os componentes disponíveis
const componentsMap = {
  profile: UserProfile,
  products: AdminProducts,
  storeProducts: AdminStoreProducts,
  plans: AdminPlans,
  //orders: Orders,
  //settings: Settings,
};

// Determina o componente a ser renderizado com base no parâmetro 'view'
const currentComponent = computed(() => {
  const view = route.query.view || 'profile'; // 'profile' como padrão
  return componentsMap[view] || UserProfile; // Fallback para UserProfile
});

// Verifica se o usuário é admin ao carregar a página
onMounted(async () => {
  if (!authStore.isAdmin) {
    console.warn('Acesso não autorizado - redirecionando');
    await navigateTo('/');
  }
});
</script>

<style lang="scss" scoped>


.error-message {
  color: #e74c3c;
  font-weight: bold;
  padding: 1rem;
  background-color: #fde8e8;
  border-radius: 4px;
}
</style>