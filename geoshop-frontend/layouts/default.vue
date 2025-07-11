<template>
  <v-app>
    <v-app-bar app color="white" elevation="1">
      <v-toolbar-title class="font-weight-bold text-primary">GeoShop</v-toolbar-title>
      <v-spacer></v-spacer>
      
      <!-- Apenas mostra o menu do usuário quando logado -->
      <template v-if="authStore.user">
        <v-menu open-on-hover>
          <template v-slot:activator="{ props }">
            <div v-bind="props" class="avatar-activator">
              <v-avatar size="40" color="transparent">
                <v-img v-if="authStore.user.avatar" :src="authStore.user.avatar"></v-img>
                <v-icon v-else color="grey-darken-1">mdi-account-circle</v-icon>
              </v-avatar>
            </div>
          </template>
          
          <v-card width="300" elevation="4">
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-avatar size="48" class="mr-3">
                    <v-img v-if="authStore.user.avatar" :src="authStore.user.avatar"></v-img>
                    <v-icon v-else size="48">mdi-account-circle</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-bold">{{ authStore.user.username }}</v-list-item-title>
                <v-list-item-subtitle>{{ authStore.user.email }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-divider class="my-2"></v-divider>
              
              <v-list-item v-if="authStore.user.user_type">
                <template v-slot:prepend>
                  <v-icon class="mr-3">mdi-account-tie</v-icon>
                </template>
                <v-list-item-title>{{ getUserTypeText(authStore.user.user_type) }}</v-list-item-title>
              </v-list-item>
              
              <v-list-item @click="navigateTo('store/profile')">
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
    
    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth';
import { navigateTo } from '#app';

const authStore = useAuthStore();

const handleLogout = async () => {
  try {
    await authStore.logout();
    await navigateTo('/login');
  } catch (error) {
    console.error('Erro ao fazer logout:', error);
  }
};

const getUserTypeText = (type: string) => {
  const types = {
    client: 'Cliente',
    store: 'Loja',
    admin: 'Administrador'
  };
  return types[type] || type;
};
</script>

<style scoped>
.avatar-activator {
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.avatar-activator:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-app-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12) !important;
}

.text-primary {
  color: #6200ee;
}

.text-error {
  color: #b00020;
}

.v-list-item {
  cursor: pointer;
  min-height: 48px;
}

.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}
</style>