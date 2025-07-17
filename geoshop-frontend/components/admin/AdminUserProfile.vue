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
                  <th>Plano</th>
                  <th>Telefone</th>
                  <th>Responsável</th>
                  <th>Qtd. Mínima</th>
                  <th>Cartão Fidelidade</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in paginatedUsers" :key="user.id">
                  <td>{{ user.username }}</td>
                  <td>{{ user.email || 'Não informado' }}</td>
                  <td>
                    <span v-if="user.active_plan">{{ user.active_plan.name }}</span>
                    <span v-else>Nenhum</span>
                  </td>
                  <td>{{ user.phone || 'N/A' }}</td>
                  <td>{{ user.responsible || 'N/A' }}</td>
                  <td>
                    <v-icon v-if="user.use_bulk_pricing" left color="success">
                      mdi-check-circle-outline
                    </v-icon>
                    <v-icon v-else left color="error">
                      mdi-alpha-x-circle-outline
                    </v-icon>
                  </td>
                  <td>
                    <v-icon v-if="user.has_loyalty_card" left color="success">
                      mdi-check-circle-outline
                    </v-icon>
                    <v-icon v-else left color="error">
                      mdi-alpha-x-circle-outline
                    </v-icon>
                  </td>
                  <td>
                    <div class="d-flex">
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openDetailsModal(user)"
                      >
                        <v-icon left>mdi-eye</v-icon>
                        Detalhes
                      </v-btn>
                      <v-btn
                        color="primary"
                        variant="text"
                        size="small"
                        class="mr-2"
                        @click="openEditModal(user)"
                      >
                        <v-icon left>mdi-pencil</v-icon>
                        Editar
                      </v-btn>
                      <v-btn
                        color="error"
                        variant="text"
                        size="small"
                        @click="confirmDeleteUser(user)"
                      >
                        <v-icon left>mdi-delete</v-icon>
                        Excluir
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

        <!-- Modal de Detalhes -->
        <v-dialog v-model="detailsModal" max-width="600">
          <v-card>
            <v-card-title class="text-h5 font-weight-bold text-primary">
              Detalhes da Loja
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <p><strong>Nome:</strong> {{ selectedUser.username || 'N/A' }}</p>
                  <p><strong>Plano:</strong> {{ selectedUser.active_plan?.name || 'Nenhum' }}</p>
                  <p v-if="selectedUser.active_plan">
                    <strong>Limite de Produtos:</strong> {{ selectedUser.active_plan.product_limit }}
                  </p>
                  <p><strong>Responsável:</strong> {{ selectedUser.responsible || 'N/A' }}</p>
                  <p><strong>E-mail:</strong> {{ selectedUser.email || 'N/A' }}</p>
                  <p><strong>Telefone:</strong> {{ selectedUser.phone || 'N/A' }}</p>
                  <p><strong>CNPJ:</strong> {{ selectedUser.cnpj || 'N/A' }}</p>
                  <p><strong>Endereço:</strong> {{ selectedUser.address || 'N/A' }}</p>
                  <p><strong>Trabalha com Qtd. Mínima:</strong> 
                    {{ selectedUser.use_bulk_pricing ? 'Sim' : 'Não' }}
                  </p>
                  <p><strong>Cartão Fidelidade:</strong> 
                    {{ selectedUser.has_loyalty_card ? 'Sim' : 'Não' }}
                  </p>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions class="justify-end">
              <v-btn color="grey" @click="detailsModal = false">
                Fechar
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Modal de Edição -->
        <v-dialog v-model="editModal" max-width="800" persistent>
          <v-card>
            <v-card-title class="text-h4 font-weight-bold text-primary">
              Editar Usuário
            </v-card-title>
            <v-card-text>
              <v-form @submit.prevent="submitForm" ref="form">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="editForm.username"
                      label="Nome do Usuário"
                      :prepend-inner-icon="
                        editForm.user_type === 'store' ? 'mdi-store' : 
                        editForm.user_type === 'admin' ? 'mdi-account-tie' : 
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
                      :prepend-inner-icon="editForm.user_type === 'store' ? 'mdi-store' : 
                                           editForm.user_type === 'admin' ? 'mdi-account-tie' : 
                                           'mdi-account'"
                      :items="['admin', 'store', 'client']"
                      outlined
                      :rules="[v => !!v || 'Tipo de usuário é obrigatório']"
                    />
                    <v-select
                      v-if="editForm.user_type === 'store'"
                      v-model="editForm.active_plan"
                      label="Plano Ativo"
                      prepend-inner-icon="mdi-credit-card-outline"
                      :items="planOptions"
                      item-title="name"
                      item-value="id"
                      return-object
                      outlined
                      clearable
                    >
                      <template v-slot:item="{ props, item }">
                        <v-list-item
                          v-bind="props"
                          :title="item.raw.name"
                          :subtitle="`Limite: ${item.raw.product_limit} | R$ ${item.raw.price}`"
                        ></v-list-item>
                      </template>
                    </v-select>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-if="editForm.user_type === 'store'"
                      v-model="editForm.cnpj"
                      label="CNPJ"
                      prepend-inner-icon="mdi-file-document"
                      v-mask="'##.###.###/####-##'"
                      outlined
                      :rules="[v => !v || /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(v) || 'CNPJ inválido']"
                    />
                    <v-text-field
                      v-if="editForm.user_type === 'store'"
                      v-model="editForm.address"
                      label="Endereço"
                      prepend-inner-icon="mdi-map-marker"
                      outlined
                    />
                    <v-text-field
                      v-if="editForm.user_type === 'store'"
                      v-model="editForm.responsible"
                      label="Responsável"
                      prepend-inner-icon="mdi-account"
                      outlined
                    />
                    <v-text-field
                      v-if="editForm.user_type === 'store'"
                      v-model="editForm.phone"
                      label="Telefone"
                      prepend-inner-icon="mdi-phone"
                      v-mask="'+55 (##) #####-####'"
                      outlined
                    />
                    <template v-if="editForm.user_type === 'store'">
                      <v-checkbox
                        v-model="editForm.use_bulk_pricing"
                        label="Trabalha com quantidade mínima?"
                        class="mt-2"
                      ></v-checkbox>
                      <v-checkbox
                        v-model="editForm.has_loyalty_card"
                        label="Oferece cartão fidelidade?"
                        class="mt-2"
                      ></v-checkbox>
                    </template>
                  </v-col>
                </v-row>
                <v-card-actions class="justify-end mt-4">
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
                </v-card-actions>
              </v-form>
            </v-card-text>
          </v-card>
        </v-dialog>

        <!-- Modal de Confirmação de Exclusão -->
        <v-dialog v-model="confirmDelete" max-width="500" persistent>
          <v-card>
            <v-card-title class="text-h5 font-weight-bold text-primary">
              Confirmar Exclusão
            </v-card-title>
            <v-card-text>
              Tem certeza que deseja excluir o usuário <strong>{{ editForm.username }}</strong>? Esta ação não pode ser desfeita.
            </v-card-text>
            <v-card-actions class="justify-end">
              <v-btn color="grey" @click="confirmDelete = false">Cancelar</v-btn>
              <v-btn color="error" @click="deleteUser" :loading="deleting">
                Confirmar Exclusão
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

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

// Variáveis reativas
const activeTab = ref('all');
const page = ref(1);
const itemsPerPage = ref(10);
const searchQuery = ref('');
const detailsModal = ref(false);
const selectedUser = ref({});
const planOptions = ref([]);
const loading = ref(false);
const deleting = ref(false);
const editModal = ref(false);
const confirmDelete = ref(false);
const error = ref('');
const form = ref(null);

// Formulário de edição
const editForm = ref({
  id: null,
  username: '',
  email: '',
  user_type: '',
  cnpj: '',
  address: '',
  responsible: '',
  phone: '',
  use_bulk_pricing: false,
  has_loyalty_card: false,
  active_plan: null
});

// Busca com debounce
const debouncedSearch = debounce(() => {
  page.value = 1;
}, 500);

// Filtra usuários
const filteredUsers = computed(() => {
  let users = authStore.users;
  
  if (activeTab.value !== 'all') {
    users = users.filter(user => user.user_type === activeTab.value);
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    users = users.filter(user => 
      (user.username && user.username.toLowerCase().includes(query)) ||
      (user.email && user.email.toLowerCase().includes(query)) ||
      (user.cnpj && user.cnpj.includes(query)) ||
      (user.responsible && user.responsible.toLowerCase().includes(query)) ||
      (user.phone && user.phone.includes(query))
    );
  }
  
  return users;
});

// Calcula total de páginas
const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value);
});

// Paginação
const paginatedUsers = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredUsers.value.slice(start, end);
});

// Validação do formulário
const editFormValid = computed(() => {
  return (
    !!editForm.value.username &&
    !!editForm.value.email &&
    /.+@.+\..+/.test(editForm.value.email) &&
    !!editForm.value.user_type
  );
});

// Carrega usuários
const loadUsers = async () => {
  try {
    loading.value = true;
    await authStore.fetchAllUsers();
  } catch (err) {
    error.value = 'Erro ao carregar lista de usuários';
    console.error('Erro ao carregar usuários:', err);
  } finally {
    loading.value = false;
  }
};

// Carrega planos
const fetchPlans = async () => {
  try {
    const planStore = usePlanStore();
    await planStore.fetchPlans();
    planOptions.value = planStore.plans;
  } catch (err) {
    error.value = 'Erro ao carregar planos disponíveis';
    console.error('Erro ao carregar planos:', err);
  }
};

// Formata tipo de usuário
const formatUserType = (type) => {
  const types = {
    admin: 'Administrador',
    store: 'Loja',
    client: 'Cliente',
  };
  return types[type] || type;
};

// Abre modal de detalhes
const openDetailsModal = (user) => {
  selectedUser.value = JSON.parse(JSON.stringify(user));
  detailsModal.value = true;
};

// Abre modal de edição
const openEditModal = (user) => {
  editForm.value = {
    id: user.id,
    username: user.username || '',
    email: user.email || '',
    user_type: user.user_type || '',
    cnpj: user.cnpj || '',
    address: user.address || '',
    responsible: user.responsible || '',
    phone: user.phone || '',
    use_bulk_pricing: user.use_bulk_pricing || false,
    has_loyalty_card: user.has_loyalty_card || false,
    active_plan: user.active_plan || null
  };
  editModal.value = true;
};

// Confirma exclusão
const confirmDeleteUser = (user) => {
  editForm.value = { ...user };
  confirmDelete.value = true;
};

// Submete formulário
const submitForm = async () => {
  const { valid } = await form.value.validate();
  if (valid) {
    try {
      loading.value = true;
      error.value = '';
      
      const formData = { 
        ...editForm.value,
        active_plan_id: editForm.value.active_plan?.id || null
      };
      
      if (formData.user_type !== 'store') {
        delete formData.cnpj;
        delete formData.address;
        delete formData.responsible;
        delete formData.phone;
        delete formData.use_bulk_pricing;
        delete formData.has_loyalty_card;
        delete formData.active_plan_id;
      }
      
      await authStore.updateUser(formData);
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

// Exclui usuário
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

// Configuração da página
definePageMeta({
  middleware: ['auth'],
});

// Carrega dados ao montar o componente
onMounted(async () => {
  if (!authStore.isAdmin) {
    return navigateTo('/');
  }
  await loadUsers();
  await fetchPlans();
});
</script>

<style lang="scss" scoped>
.admin-container {
  min-height: 100vh;
  padding: 20px;
  margin: 0;
  width: 100%;
  background: #fff;

  h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
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
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 16px;
  width: 100%;
  max-width: 500px;

  .search-field {
    width: 100%;
  }
}

.users-table {
  width: 100%;
  margin-top: 1rem;

  th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
  }

  tr:hover {
    background-color: #f8f9fa;
  }
}

.v-btn {
  text-transform: none;
  letter-spacing: normal;
  font-weight: 500;
}

.v-text-field {
  margin-bottom: 12px;
}

@media (max-width: 600px) {
  .admin-container {
    padding: 10px;
  }

  .text-h4 {
    font-size: 1.5rem !important;
  }

  .users-table {
    font-size: 0.8rem;
  }

  .v-btn {
    min-width: 36px !important;
    padding: 0 8px !important;
    font-size: 0.75rem;
  }
  
  .controls {
    flex-direction: column;
    
    .search-field {
      max-width: 100%;
    }
  }
}
</style>