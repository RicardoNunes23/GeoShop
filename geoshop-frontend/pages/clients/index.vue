<template>
  <div class="client-container">
    <p v-if="!authStore.isClient" class="error-message">
      Acesso restrito a clientes
    </p>
    <div v-else>
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth';
import { useRoute, useRouter } from '#app';
import { computed, onMounted } from 'vue';
import ClientProfile from '~/components/client/ClientProfile.vue';
import ClientProducts from '~/components/client/ClientProducts.vue';

definePageMeta({
  middleware: ['auth'],
  layout: 'sidebar',
});

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const componentsMap = {
  profile: ClientProfile,
  products: ClientProducts,
 
};

const currentComponent = computed(() => {
  const view = route.query.view || 'profile';
  return componentsMap[view] || ClientProfile;
});

onMounted(async () => {
  if (!authStore.isClient) {
    await router.push('/');
  } else if (!authStore.user) {
    try {
      await authStore.fetchClientProfile();
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
    }
  }
});
</script>

<style scoped>
.error-message {
  color: #e74c3c;
  font-weight: bold;
  padding: 1rem;
  background-color: #fde8e8;
  border-radius: 4px;
}
</style>