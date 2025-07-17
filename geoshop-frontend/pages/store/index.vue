<template>
  <div class="store-container">
    <p v-if="!authStore.isStore" class="error-message">
      Acesso restrito a lojas
    </p>
    <div v-else>
      <component :is="currentComponent" />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth';
import { useRoute, useRouter } from '#app';
import { computed, onMounted } from 'vue';
import StoreProfile from '../components/store/StoreProfile.vue';
import StoreProducts from '../components/store/StoreProducts.vue';

definePageMeta({
  middleware: ['auth'],
  layout: 'sidebar',
});

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const componentsMap = {
  profile: StoreProfile,
  products: StoreProducts,
  //orders: Orders,
  //settings: Settings,
};

const currentComponent = computed(() => {
  const view = route.query.view || 'profile';
  return componentsMap[view] || ProfileStore;
});

onMounted(async () => {
  if (!authStore.isStore) {
    console.warn('Acesso não autorizado - redirecionando');
    await router.push('/');
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