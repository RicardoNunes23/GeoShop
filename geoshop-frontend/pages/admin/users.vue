<template>
  <div class="admin-container">
    <h1>Painel Administrativo</h1>
    <p v-if="!authStore.isAdmin" class="error-message">
      Acesso restrito a administradores
    </p>
    
    <div v-else>
      <div class="controls">
        <v-btn
          @click="refreshUsers"
          color="primary"
          prepend-icon="mdi-refresh"
        >
          Atualizar Lista
        </v-btn>
      </div>

      <v-progress-linear
        v-if="loading"
        indeterminate
        color="primary"
        class="my-4"
      ></v-progress-linear>
      
      <div v-else>
        <v-table class="users-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Tipo</th>
              <th>CNPJ (Lojas)</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in authStore.users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email || 'Não informado' }}</td>
              <td>{{ formatUserType(user.user_type) }}</td>
              <td>{{ user.cnpj || 'N/A' }}</td>
              <td>
                <v-btn
                  @click="viewUserDetails(user)"
                  color="primary"
                  variant="text"
                  size="small"
                >
                  Detalhes
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth';

const authStore = useAuthStore();
const loading = ref(false);
const router = useRouter();

definePageMeta({
  middleware: ['auth'],

});

// Verifica se o usuário é admin ao carregar a página
onMounted(async () => {
  if (!authStore.isAdmin) {
    console.warn('Acesso não autorizado - redirecionando');
    return navigateTo('/');
  }
  
  await loadUsers();
});

// Função para carregar os usuários
const loadUsers = async () => {
  try {
    loading.value = true;
    await authStore.fetchAllUsers();
  } catch (error) {
    console.error('Erro ao carregar usuários:', error);
    alert('Erro ao carregar lista de usuários');
  } finally {
    loading.value = false;
  }
};

// Atualiza a lista de usuários
const refreshUsers = () => {
  loadUsers();
};

// Formata o tipo de usuário para exibição
const formatUserType = (type) => {
  const types = {
    admin: 'Administrador',
    store: 'Loja',
    client: 'Cliente'
  };
  return types[type] || type;
};

// Visualizar detalhes do usuário
const viewUserDetails = (user) => {
  router.push(`/admin/users/${user.id}`);
};
</script>

<style lang="scss" scoped>
.admin-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;

  h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
  }
}

.error-message {
  color: #e74c3c;
  font-weight: bold;
  padding: 1rem;
  background-color: #fde8e8;
  border-radius: 4px;
}

.controls {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: flex-end;
}

.users-table {
  width: 100%;
  margin-top: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
  }

  tr:hover {
    background-color: #f8f9fa;
  }
}
</style>