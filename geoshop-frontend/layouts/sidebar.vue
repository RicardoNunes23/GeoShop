<template>
  <v-app>
    <!-- Barra superior -->
    <v-app-bar app color="white" elevation="2" class="modern-app-bar">
      <v-btn
        icon
        class="d-md-none"
        @click="drawer = !drawer"
        aria-label="Abrir ou fechar menu lateral"
      >
        <v-icon>mdi-menu</v-icon>
      </v-btn>
      <v-toolbar-title class="font-weight-bold text-primary">GeoShop</v-toolbar-title>
      <v-spacer></v-spacer>
      <template v-if="authStore.user">
        <v-menu open-on-hover offset-y>
          <template v-slot:activator="{ props }">
            <div v-bind="props" class="avatar-activator">
              <v-avatar size="40" color="grey-lighten-2">
                <v-img v-if="authStore.user.avatar" :src="authStore.user.avatar"></v-img>
                <v-icon v-else color="grey-darken-1">mdi-account-circle</v-icon>
              </v-avatar>
            </div>
          </template>
          <v-card width="300" elevation="4" class="modern-card">
            <v-list dense>
              <v-list-item>
                <template v-slot:prepend>
                  <v-avatar size="48" class="mr-3">
                    <v-img v-if="authStore.user.avatar" :src="authStore.user.avatar"></v-img>
                    <v-icon v-else size="48">mdi-account-circle</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-bold text-primary">
                  {{ authStore.user.username }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-grey-darken-1">
                  {{ authStore.user.email }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-divider class="my-2"></v-divider>
              <v-list-item v-if="authStore.user.user_type">
                <template v-slot:prepend>
                  <v-icon class="mr-3">mdi-account-tie</v-icon>
                </template>
                <v-list-item-title>{{ getUserTypeText(authStore.user.user_type) }}</v-list-item-title>
              </v-list-item>
              <v-list-item @click="navigateTo(authStore.user.user_type === 'store' ? '/store?view=profile' : '/admin')">
                <template v-slot:prepend>
                  <v-icon class="mr-3">mdi-account-cog</v-icon>
                </template>
                <v-list-item-title>Meu Perfil</v-list-item-title>
              </v-list-item>
              <v-divider class="my-2"></v-divider>
              <v-list-item @click="handleLogout" class="text-error">
                <template v-slot:prepend>
                  <v-icon class="mr-3">mdi-logout</v-icon>
                </template>
                <v-list-item-title>Sair</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card>
        </v-menu>
      </template>
    </v-app-bar>

    <!-- Menu lateral -->
    <v-navigation-drawer
      app
      v-model="drawer"
      :temporary="$vuetify.display.mdAndDown"
      color="white"
      elevation="2"
      class="modern-drawer"
    >
      <v-list dense class="pt-4">
        <v-list-item
          v-for="(item, index) in sidebarItems"
          :key="index"
          @click="navigateTo(item.route); drawer = $vuetify.display.mdAndDown ? false : drawer"
          class="modern-list-item"
          :active="isActive(item)"
        >
          <template v-slot:prepend>
            <v-icon class="mr-3">{{ item.icon }}</v-icon>
          </template>
          <v-list-item-title class="font-weight-medium">{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Conteúdo principal -->
    <v-main>
      <v-container fluid class="pa-6">
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth';
import { navigateTo, useRoute } from '#app';
import { ref } from 'vue';

// Estado do layout
const authStore = useAuthStore();
const route = useRoute();
const drawer = ref(true);

// Itens da barra lateral com base no tipo de usuário
const sidebarItems = computed(() => {
  if (authStore.user?.user_type === 'admin') {
    return [
      { title: 'Usuários', icon: 'mdi-account-group', route: '/admin?view=profile' },
      { title: 'Produtos', icon: 'mdi-cart', route: '/admin?view=products' },
      { title: 'Pedidos', icon: 'mdi-clipboard-list', route: '/orders' },
      { title: 'Listas', icon: 'mdi-plus', route: '/admin?view=storeProducts' },
      { title: 'Configurações', icon: 'mdi-cog', route: '/settings' },
    ];
  } else if (authStore.user?.user_type === 'store') {
    return [
      { title: 'Meu cadastro', icon: 'mdi-account-outline', route: '/store?view=profile' },
      { title: 'Produtos', icon: 'mdi-cart', route: '/store?view=products' },
      { title: 'Pedidos', icon: 'mdi-clipboard-list', route: '/store?view=orders' },
      { title: 'Listas de Itens', icon: 'mdi-plus', route: '/store?view=orders' },
      { title: 'Configurações', icon: 'mdi-cog', route: '/store?view=settings' },
    ];
  }
  return [];
});

// Determina se o item está ativo
function isActive(item) {
  if (authStore.user?.user_type === 'store') {
    const currentView = route.query.view || 'profile';
    return route.path === '/store' && item.route.includes(`view=${currentView}`);
  }
  return route.path === item.route;
}

// Função de logout
const handleLogout = async () => {
  try {
    await authStore.logout();
    await navigateTo('/login');
  } catch (error) {
    console.error('Erro ao fazer logout:', error);
  }
};

// Texto para tipo de usuário
const getUserTypeText = (type: string) => {
  const types = {
    client: 'Cliente',
    store: 'Loja',
    admin: 'Administrador',
  };
  return types[type] || type;
};
</script>

<style scoped>
.modern-app-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
  backdrop-filter: blur(8px);
}

.avatar-activator {
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.avatar-activator:hover {
  background-color: rgba(0, 0, 0, 0.06);
  transform: scale(1.05);
}

.text-primary {
  color: #3b82f6 !important;
  font-family: 'Inter', sans-serif;
}

.text-error {
  color: #ef4444 !important;
}

.modern-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.08) !important;
  transition: transform 0.3s ease-in-out;
}

.modern-list-item {
  border-radius: 8px !important;
  margin: 0 8px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.modern-list-item:hover {
  background-color: rgba(59, 130, 246, 0.1);
  transform: translateX(4px);
}

.modern-list-item.v-list-item--active {
  background-color: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.modern-card {
  border-radius: 12px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.v-list-item-title {
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
}
</style>