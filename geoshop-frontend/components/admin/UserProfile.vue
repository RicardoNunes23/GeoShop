<template>
  <div class="admin-container">
    
    <h1><v-icon start>mdi-account-group-outline</v-icon>Usuários</h1>
    <p v-if="!authStore.isAdmin" class="error-message">
      Acesso restrito a administradores
    </p>
    
    <div v-else>
      <div class="controls">
       <v-text-field
          v-model="searchQuery"
          label="Buscar usuários"
          prepend-inner-icon="mdi-magnify"
          outlined
          dense
          class="search-field"
          @input="debouncedSearch"
        />
      </div>

      <v-progress-linear
        v-if="loading"
        indeterminate
        color="primary"
        class="my-4"
      ></v-progress-linear>
      
      <div v-else>
        <v-tabs v-model="activeTab" grow>
          <!-- <v-tab value="all">
            <v-icon start>mdi-account-multiple</v-icon>
            Todos
          </v-tab> -->
          <v-tab value="admin">
            <v-icon start>mdi-account-tie</v-icon>
            Administradores
          </v-tab>
          <v-tab value="store">
            <v-icon start>mdi-store</v-icon>
            Lojas
          </v-tab>
          <v-tab value="client">
            <v-icon start>mdi-account</v-icon>
            Clientes
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-4">
          <!-- <v-window-item value="all">
            <v-table class="users-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>CNPJ (Lojas)</th>
                  <th>Endereço</th>
                  <th>Responsável</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || 'Não informado' }}</td>
                  <td>{{ formatUserType(user.user_type) }}</td>
                  <td>{{ user.cnpj || 'N/A' }}</td>
                  <td>{{ user.address || 'N/A' }}</td>
                  <td>{{ user.responsible || 'N/A' }}</td>
                  <td>
                    <div class="d-flex">
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openEditModal(user)"
                      >
                        <v-icon left>mdi-pencil</v-icon>
                      
                      </v-btn>
                      <v-btn
                        color="error"
                        variant="text"
                        size="small"
                        @click="confirmDeleteUser(user)"
                      >
                        <v-icon left>mdi-delete</v-icon>
                       
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <v-pagination
              v-model="page"
              :length="totalPages"
              :total-visible="7"
              class="mt-4"
            ></v-pagination>
          </v-window-item> -->
          
          <v-window-item value="admin">
            <v-table class="users-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || 'Não informado' }}</td>
                  <td>{{ formatUserType(user.user_type) }}</td>
                 
                  <td>
                    <div class="d-flex">
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openEditModal(user)"
                      >
                        <v-icon left>mdi-pencil</v-icon>
                       
                      </v-btn>
                      <v-btn
                        color="error"
                        variant="text"
                        size="small"
                        @click="confirmDeleteUser(user)"
                      >
                        <v-icon left>mdi-delete</v-icon>
                        
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <v-pagination
              v-model="page"
              :length="totalPages"
              :total-visible="7"
              class="mt-4"
            ></v-pagination>
          </v-window-item>
          
          <v-window-item value="store">
            <v-table class="users-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>CNPJ</th>
                  <th>Endereço</th>
                  <th>Responsável</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || 'Não informado' }}</td>
                  <td>{{ formatUserType(user.user_type) }}</td>
                  <td>{{ user.cnpj || 'N/A' }}</td>
                  <td>{{ user.address || 'N/A' }}</td>
                  <td>{{ user.responsible || 'N/A' }}</td>
                  <td>
                    <div class="d-flex">
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openEditModal(user)"
                      >
                        <v-icon left>mdi-pencil</v-icon>
                       
                      </v-btn>
                      <v-btn
                        color="error"
                        variant="text"
                        size="small"
                        @click="confirmDeleteUser(user)"
                      >
                        <v-icon left>mdi-delete</v-icon>
                        
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <v-pagination
              v-model="page"
              :length="totalPages"
              :total-visible="7"
              class="mt-4"
            ></v-pagination>
          </v-window-item>
          
          <v-window-item value="client">
            <v-table class="users-table">
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || 'Não informado' }}</td>
                  <td>{{ formatUserType(user.user_type) }}</td>
                 
                  <td>
                    <div class="d-flex">
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openEditModal(user)"
                      >
                        <v-icon left>mdi-pencil</v-icon>
                       
                      </v-btn>
                      <v-btn
                        color="error"
                        variant="text"
                        size="small"
                        @click="confirmDeleteUser(user)"
                      >
                        <v-icon left>mdi-delete</v-icon>
                        
                      </v-btn>
                    </div>
                  </td>
                </tr>
              </tbody>
            </v-table>
            <v-pagination
              v-model="page"
              :length="totalPages"
              :total-visible="7"
              class="mt-4"
            ></v-pagination>
          </v-window-item>
        </v-window>
      </div>

      <!-- Modal de Edição -->
      <v-dialog v-model="editModal" max-width="800" persistent>
        <div class="modal-content">
          <h2 class="text-h4 font-weight-bold text-primary">
            Editar Usuário
          </h2>
          <v-form @submit.prevent="submitForm" ref="form">
            <v-row>
              <v-col cols="12" md="6">
                 <v-text-field
                    v-model="editForm.username"
                    label="Nome do Usuário"
                    :prepend-inner-icon="
                      editForm.user_type === 'store' ? 'mdi-store' : 
                      editForm.user_type === 'admin' ? 'mdi-accoun' : 
                      'mdi-account'
                    "
                    outlined
                    :rules="[v => !!v || 'Nome do usuário é obrigatório']"
                  />
                <v-text-field
                  v-model="editForm.email"
                  label="E-mail"
                  prepend-inner-icon="mdi-email"
                  type="email"
                  outlined
                  :rules="[v => !!v || 'E-mail é obrigatório', v => /.+@.+\..+/.test(v) || 'E-mail inválido']"
                />
                <v-select
                  v-model="editForm.user_type"
                  label="Tipo de Usuário"
                  :prepend-inner-icon="editForm.user_type === 'store' ? 'mdi-store' : 'mdi-account'"
                  :items="['admin', 'store', 'client']"
                  outlined
                  :rules="[v => !!v || 'Tipo de usuário é obrigatório']"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editForm.cnpj"
                  label="CNPJ"
                  prepend-inner-icon="mdi-file-document"
                  v-mask="'##.###.###/####-##'"
                  outlined
                  :rules="[v => !v || /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(v) || 'CNPJ inválido']"
                />
                <v-text-field
                  v-model="editForm.address"
                  label="Endereço"
                  prepend-inner-icon="mdi-map-marker"
                  outlined
                />
                <v-text-field
                  v-model="editForm.responsible"
                  label="Responsável"
                  prepend-inner-icon="mdi-account"
                  outlined
                />
              </v-col>
            </v-row>
            <div class="justify-end mt-4 d-flex">
              <v-btn color="grey" @click="editModal = false">
                Cancelar
              </v-btn>
              <v-btn
                type="submit"
                color="primary"
                :loading="loading"
                :disabled="!editFormValid"
              >
                <v-icon left>mdi-content-save</v-icon>
                Salvar Alterações
              </v-btn>
            </div>
          </v-form>
        </div>
      </v-dialog>

      <!-- Modal de Confirmação de Exclusão -->
      <v-dialog v-model="confirmDelete" max-width="500" persistent>
        <div class="modal-content">
          <h2 class="text-h5 font-weight-bold text-primary">
            Confirmar Exclusão
          </h2>
          <p>
            Tem certeza que deseja excluir o usuário <strong>{{ editForm.username }}</strong>? Esta ação não pode ser desfeita.
          </p>
          <div class="d-flex justify-end">
            <v-btn text @click="confirmDelete = false">Cancelar</v-btn>
            <v-btn color="error" @click="deleteUser" :loading="deleting">
              Confirmar
            </v-btn>
          </div>
        </div>
      </v-dialog>

      <!-- Alerta de erro ou sucesso -->
      <v-alert
        v-if="error"
        :type="error.includes('sucesso') ? 'success' : 'error'"
        variant="tonal"
        class="mt-4 mb-6"
        dismissible
      >
        {{ error }}
      </v-alert>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth';
import { ref, computed, onMounted } from 'vue';
import { useRouter } from '#app';
import { mask } from 'vue-the-mask';
import { debounce } from 'lodash-es';

const authStore = useAuthStore();
const router = useRouter();

// Estados para abas, paginação e pesquisa
const activeTab = ref('all');
const page = ref(1);
const itemsPerPage = ref(10);
const searchQuery = ref('');

// Estados existentes
const loading = ref(false);
const deleting = ref(false);
const editModal = ref(false);
const confirmDelete = ref(false);
const error = ref('');
const form = ref(null);
const editForm = ref({
  id: null,
  username: '',
  email: '',
  user_type: '',
  cnpj: '',
  address: '',
  responsible: '',
});

// Debounce para pesquisa
const debouncedSearch = debounce(() => {
  page.value = 1; // Resetar para a primeira página ao pesquisar
}, 500);

// Filtra usuários por tipo e pesquisa
const filteredUsers = computed(() => {
  let users = authStore.users;
  
  // Filtro por tipo de usuário
  if (activeTab.value !== 'all') {
    users = users.filter(user => user.user_type === activeTab.value);
  }
  
  // Filtro por texto de pesquisa
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    users = users.filter(user => 
      (user.username && user.username.toLowerCase().includes(query)) ||
      (user.email && user.email.toLowerCase().includes(query)) ||
      (user.cnpj && user.cnpj.includes(query)) ||
      (user.responsible && user.responsible.toLowerCase().includes(query))
    );
  }
  
  return users;
});

// Paginação
const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value);
});

const paginatedUsers = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredUsers.value.slice(start, end);
});

// Métodos existentes (mantidos iguais)
const loadUsers = async () => {
  try {
    loading.value = true;
    await authStore.fetchAllUsers();
  } catch (error) {
    console.error('Erro ao carregar usuários:', error);
    error.value = 'Erro ao carregar lista de usuários';
  } finally {
    loading.value = false;
  }
};

const refreshUsers = () => {
  loadUsers();
};

const formatUserType = (type) => {
  const types = {
    admin: 'Administrador',
    store: 'Loja',
    client: 'Cliente',
  };
  return types[type] || type;
};

const openEditModal = (user) => {
  editForm.value = {
    id: user.id,
    username: user.username || '',
    email: user.email || '',
    user_type: user.user_type || '',
    cnpj: user.cnpj || '',
    address: user.address || '',
    responsible: user.responsible || '',
  };
  editModal.value = true;
};

const confirmDeleteUser = (user) => {
  editForm.value = { ...user };
  confirmDelete.value = true;
};

const submitForm = async () => {
  const { valid } = await form.value.validate();
  if (valid) {
    try {
      loading.value = true;
      error.value = '';
      await authStore.updateUser(editForm.value);
      await loadUsers();
      editModal.value = false;
      error.value = 'Usuário atualizado com sucesso!';
    } catch (err) {
      error.value = err.message || 'Erro ao atualizar usuário';
    } finally {
      loading.value = false;
    }
  } else {
    error.value = 'Por favor, corrija os erros no formulário.';
  }
};

const deleteUser = async () => {
  try {
    deleting.value = true;
    error.value = '';
    await authStore.deleteUser(editForm.value.id);
    await loadUsers();
    confirmDelete.value = false;
    error.value = 'Usuário excluído com sucesso!';
  } catch (err) {
    error.value = err.message || 'Erro ao excluir usuário';
  } finally {
    deleting.value = false;
  }
};

definePageMeta({
  middleware: ['auth'],
});

onMounted(async () => {
  if (!authStore.isAdmin) {
    return navigateTo('/');
  }
  await loadUsers();
});
</script>

<style lang="scss" scoped>
.admin-container {
  min-height: 100vh;
  padding: 0;
  margin: 0;
  width: 100%;
  background: #fff;
  border: none;

  h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
    padding: 1rem;
  }
}

.error-message {
  color: #e74c3c;
  font-weight: bold;
  padding: 1rem;
  background-color: #fde8e8;
}

.controls {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 16px;
  width: 40%; 
}

.users-table {
  width: 100%;
  margin-top: 1rem;
  border: none;

  th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
    border: none;
  }

  tr {
    border: none;
  }

  tr:hover {
    background-color: #f8f9fa;
  }
}

.modal-content {
  padding: 16px;
  background: white;
  border: none;
}

.v-btn {
  text-transform: none;
  letter-spacing: normal;
}

.v-text-field {
  margin-bottom: 12px;
}

/* Ajustes para mobile */
@media (max-width: 600px) {
  .text-h4 {
    font-size: 1.5rem !important;
  }

  .users-table {
    font-size: 0.8rem;
  }

  .v-btn {
    min-width: 36px !important;
    padding: 0 8px !important;
  }
  
  .controls {
    flex-direction: column;
    
    .search-field {
      max-width: 100%;
    }
  }
}
</style>