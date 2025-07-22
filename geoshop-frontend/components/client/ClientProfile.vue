<template>
  <div>
    <h2 class="text-h4 font-weight-bold text-primary mb-6">
      Perfil do Cliente
    </h2>

    <!-- Tabela com AppDataTable -->
    <div class="pa-4 mb-6">
      <AppDataTable
        :key="profileKey"
        :items="[profile]"
        :headers="headers"
        :loading="loading"
        hide-empty-message
        :table-class="'no-border'"
      >
        <template v-slot:item.phone="{ item }">
          {{ formatPhone(item.phone) || 'Não informado' }}
        </template>
        <template v-slot:item.actions="{ item }">
          <AppActionButtons
            :item="item"
            @details="openDetailsModal"
            @edit="openEditModal"
            @delete="confirmDeleteProfile"
          />
        </template>
      </AppDataTable>
    </div>

    <v-alert
      v-if="error"
      :type="error.includes('sucesso') ? 'success' : 'error'"
      variant="tonal"
      class="mt-4 mb-6"
      dismissible
    >
      {{ error }}
    </v-alert>

    <!-- Modal de detalhes -->
    <v-dialog v-model="detailsModal" max-width="600" persistent>
      <div class="modal-content">
        <h2 class="text-h5 font-weight-bold text-primary mb-4">
          Detalhes do Perfil
        </h2>
        <v-card elevation="0">
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <p><strong>Nome:</strong> {{ profile.username }}</p>
                <p><strong>E-mail:</strong> {{ profile.email }}</p>
                <p><strong>Telefone:</strong> {{ formatPhone(profile.phone) || 'Não informado' }}</p>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn color="grey" @click="detailsModal = false">
              Fechar
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
    </v-dialog>

    <!-- Modal de edição -->
    <v-dialog v-model="editModal" max-width="800" persistent>
      <div class="modal-content">
        <h2 class="text-h4 font-weight-bold text-primary">
          Editar Perfil
        </h2>
        <v-form @submit.prevent="updateProfile" ref="form">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="editForm.username"
                label="Nome"
                prepend-inner-icon="mdi-account"
                outlined
                :rules="[v => !!v || 'Nome é obrigatório']"
              />
              <v-text-field
                v-model="editForm.email"
                label="E-mail"
                prepend-inner-icon="mdi-email"
                type="email"
                outlined
                :rules="[
                  v => !!v || 'E-mail é obrigatório',
                  v => /.+@.+\..+/.test(v) || 'E-mail inválido',
                ]"
              />
              <v-text-field
                v-model="editForm.phone"
                label="Telefone"
                prepend-inner-icon="mdi-phone"
                v-mask="'+55 (##) #####-####'"
                outlined
                :rules="[v => !!v || 'Telefone é obrigatório', v => /^\+55 \(\d{2}\) \d{5}-\d{4}$/.test(v) || 'Telefone inválido']"
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

    <!-- Modal de confirmação de exclusão -->
    <v-dialog v-model="confirmDelete" max-width="500" persistent>
      <div class="modal-content">
        <h2 class="text-h5 font-weight-bold text-primary">
          Confirmar Exclusão
        </h2>
        <p>
          Tem certeza que deseja excluir sua conta permanentemente? Esta ação não
          pode ser desfeita.
        </p>
        <div class="d-flex justify-end">
          <v-btn text @click="confirmDelete = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteProfile" :loading="deleting">
            Confirmar Exclusão
          </v-btn>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';
import AppDataTable from '~/components/app/AppDataTable.vue';

const authStore = useAuthStore();
const router = useRouter();

// Dados reativos
const profileKey = ref(0); // Chave para forçar re-renderização
const profile = computed(() => {
  console.log('Computed profile:', authStore.user); // Log para depuração
  return {
    username: authStore.user?.username || '',
    email: authStore.user?.email || '',
    phone: authStore.user?.phone || '',
    ...authStore.user
  };
});

const headers = ref([
  { title: 'Nome', key: 'username', sortable: true },
  { title: 'E-mail', key: 'email', sortable: true },
  { title: 'Telefone', key: 'phone', sortable: true },
  { title: '', key: 'actions', sortable: false, align: 'end' }
]);

const detailsModal = ref(false);
const editModal = ref(false);
const confirmDelete = ref(false);
const loading = ref(false);
const deleting = ref(false);
const error = ref('');

const editForm = ref({
  username: '',
  email: '',
  phone: ''
});

// Validação do formulário
const editFormValid = computed(() => {
  return (
    !!editForm.value.username &&
    !!editForm.value.email &&
    /.+@.+\..+/.test(editForm.value.email) &&
    !!editForm.value.phone &&
    /^\+55 \(\d{2}\) \d{5}-\d{4}$/.test(editForm.value.phone)
  );
});

// Função para formatar o telefone
function formatPhone(phone: string | null): string | null {
  if (!phone) return null;
  // Remove qualquer caractere não numérico
  const digits = phone.replace(/\D/g, '');
  // Verifica se o número tem 11 dígitos (DDD + número)
  if (digits.length === 11) {
    return `+55 (${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }
  return phone; // Retorna o original se não puder formatar
}

// Sincroniza o formulário com os dados do usuário
watch(
  () => authStore.user,
  (newUser) => {
    if (newUser) {
      editForm.value = {
        username: newUser.username,
        email: newUser.email,
        phone: formatPhone(newUser.phone) || ''
      };
      console.log('Watch disparado, editForm atualizado:', editForm.value); // Log para depuração
    }
  },
  { immediate: true, deep: true }
);

onMounted(async () => {
  if (!authStore.isClient) {
    await router.push('/');
  } else if (!authStore.user) {
    try {
      await authStore.fetchClientProfile();
    } catch (err) {
      console.error('Erro ao carregar perfil:', err);
      error.value = 'Erro ao carregar perfil';
    }
  }
});

function openDetailsModal() {
  detailsModal.value = true;
}

function openEditModal(item: typeof profile.value) {
  editForm.value = { ...item, phone: formatPhone(item.phone) || '' };
  editModal.value = true;
}

function confirmDeleteProfile(item: typeof profile.value) {
  editForm.value = { ...item, phone: formatPhone(item.phone) || '' };
  confirmDelete.value = true;
}

async function updateProfile() {
  try {
    loading.value = true;
    error.value = '';

    // Remove a formatação antes de enviar ao backend
    const cleanPhone = editForm.value.phone.replace(/\D/g, '');
    const formData = {
      username: editForm.value.username,
      email: editForm.value.email,
      phone: cleanPhone
    };
    console.log('Enviando dados para atualização:', formData); // Log para depuração

    await authStore.updateClientProfile(formData);
    
    editModal.value = false;
    error.value = 'Perfil atualizado com sucesso!';
    profileKey.value++; // Força re-renderização da tabela
  } catch (err: any) {
    console.error('Erro ao atualizar perfil:', err);
    error.value = err.response?.data?.message || err.message || 'Erro ao atualizar perfil';
  } finally {
    loading.value = false;
  }
}

async function deleteProfile() {
  try {
    deleting.value = true;
    error.value = '';

    await authStore.deleteProfile();
    await router.push('/');
  } catch (err: any) {
    console.error('Erro ao excluir perfil:', err);
    error.value = err.message || 'Erro ao excluir conta';
  } finally {
    deleting.value = false;
    confirmDelete.value = false;
  }
}
</script>

<style scoped>
.no-border {
  border: none !important;
  box-shadow: none !important;
}

.modal-content {
  padding: 16px;
  background: white;
}

.v-btn {
  text-transform: none;
  letter-spacing: normal;
}

.v-text-field {
  margin-bottom: 12px;
}

@media (max-width: 600px) {
  .text-h4 {
    font-size: 1.5rem !important;
  }

  .v-btn {
    min-width: 36px !important;
    padding: 0 8px !important;
  }
}
</style>