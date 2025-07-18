<!-- pages/StoreProfile.vue -->
<template>
  <div>
    <h2 class="text-h4 font-weight-bold text-primary mb-6">
      Perfil da Loja
    </h2>

    <!-- Tabela com AppDataTable -->
    <div class="pa-4 mb-6">
      <AppDataTable
        :items="[profile]"
        :headers="headers"
        :loading="loading"
        hide-empty-message
        :table-class="'no-border'"
      >
        <template v-slot:item.use_bulk_pricing="{ item }">
          {{ item.use_bulk_pricing ? 'Sim' : 'Não' }}
        </template>
        <template v-slot:item.has_loyalty_card="{ item }">
          {{ item.has_loyalty_card ? 'Sim' : 'Não' }}
        </template>
        <template v-slot:actions="{ item }">
          <div class="d-flex">
            <v-btn
              color="primary"
              class="mr-2"
              @click="openDetailsModal"
            >
              <v-icon left>mdi-eye</v-icon>
              Ver Detalhes
            </v-btn>
            <v-btn
              color="primary"
              class="mr-2"
              @click="openEditModal(item)"
            >
              <v-icon left>mdi-pencil</v-icon>
              Editar
            </v-btn>
            <v-btn
              color="error"
              @click="confirmDeleteProfile(item)"
            >
              <v-icon left>mdi-delete</v-icon>
              Excluir
            </v-btn>
          </div>
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

    <!-- Modal de detalhes da loja -->
    <v-dialog v-model="detailsModal" max-width="600" persistent>
      <div class="modal-content">
        <h2 class="text-h5 font-weight-bold text-primary mb-4">
          Detalhes da Loja
        </h2>
        <v-card elevation="0">
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <p><strong>Nome:</strong> {{ profile.username }}</p>
                <p><strong>Responsável:</strong> {{ profile.responsible }}</p>
                <p><strong>E-mail:</strong> {{ profile.email }}</p>
                <p><strong>CNPJ:</strong> {{ profile.cnpj }}</p>
                <p><strong>Endereço:</strong> {{ profile.address }}</p>
                <p><strong>Latitude:</strong> {{ profile.latitude }}</p>
                <p><strong>Longitude:</strong> {{ profile.longitude }}</p>
                <p>
                  <strong>Trabalha com Qtd. Mínima:</strong>
                  {{ profile.use_bulk_pricing ? 'Sim' : 'Não' }}
                </p>
                <p>
                  <strong>Tem Cartão Fidelidade:</strong>
                  {{ profile.has_loyalty_card ? 'Sim' : 'Não' }}
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
                label="Nome da Loja"
                prepend-inner-icon="mdi-store"
                outlined
                :rules="[v => !!v || 'Nome da loja é obrigatório']"
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
                v-model="editForm.cnpj"
                label="CNPJ"
                prepend-inner-icon="mdi-file-document"
                v-mask="'##.###.###/####-##'"
                outlined
                :rules="[
                  v => !!v || 'CNPJ é obrigatório',
                  v =>
                    /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(v) ||
                    'CNPJ inválido',
                ]"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="editForm.address"
                label="Endereço"
                prepend-inner-icon="mdi-map-marker"
                outlined
                :rules="[v => !!v || 'Endereço é obrigatório']"
              />
              <v-text-field
                v-model="editForm.responsible"
                label="Responsável"
                prepend-inner-icon="mdi-account"
                outlined
                :rules="[v => !!v || 'Responsável é obrigatório']"
              />
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="editForm.latitude"
                    label="Latitude"
                    prepend-inner-icon="mdi-latitude"
                    type="number"
                    step="0.000001"
                    outlined
                    :rules="[v => (v >= -90 && v <= 90) || 'Latitude inválida']"
                  />
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model.number="editForm.longitude"
                    label="Longitude"
                    prepend-inner-icon="mdi-longitude"
                    type="number"
                    step="0.000001"
                    outlined
                    :rules="[v => (v >= -180 && v <= 180) || 'Longitude inválida']"
                  />
                </v-col>
              </v-row>
              <v-checkbox
                v-model="editForm.use_bulk_pricing"
                label="Trabalhar com quantidade mínima?"
                class="mt-4"
              ></v-checkbox>
              <v-checkbox
                v-model="editForm.has_loyalty_card"
                label="Oferecer cartão fidelidade?"
                class="mt-2"
              ></v-checkbox>
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
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';
import { mask } from 'vue-the-mask';
import AppDataTable from '~/components/AppDataTable.vue';

const authStore = useAuthStore();
const router = useRouter();

const profile = ref({
  username: '',
  email: '',
  cnpj: '',
  address: '',
  responsible: '',
  latitude: 0,
  longitude: 0,
  use_bulk_pricing: false,
  has_loyalty_card: false,
});

const headers = ref([
  { title: 'Nome', key: 'username' },
  { title: 'Responsável', key: 'responsible' },
  { title: 'E-mail', key: 'email' },
  {
    title: 'Trabalha com Qtd. Mínima',
    key: 'use_bulk_pricing',
  },
  {
    title: 'Tem Cartão Fidelidade',
    key: 'has_loyalty_card',
  },
  { title: 'Ações', key: 'actions', sortable: false },
]);

const detailsModal = ref(false);
const editModal = ref(false);
const confirmDelete = ref(false);
const loading = ref(false);
const deleting = ref(false);
const error = ref('');

const vMask = { mounted: mask };

const editForm = ref({
  username: '',
  email: '',
  cnpj: '',
  address: '',
  responsible: '',
  latitude: 0,
  longitude: 0,
  use_bulk_pricing: false,
  has_loyalty_card: false,
});

const editFormValid = computed(() => {
  return (
    !!editForm.value.username &&
    !!editForm.value.email &&
    /.+@.+\..+/.test(editForm.value.email) &&
    !!editForm.value.cnpj &&
    /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(editForm.value.cnpj) &&
    !!editForm.value.address &&
    !!editForm.value.responsible &&
    editForm.value.latitude >= -90 &&
    editForm.value.latitude <= 90 &&
    editForm.value.longitude >= -180 &&
    editForm.value.longitude <= 180
  );
});

onMounted(async () => {
  console.log('onMounted: Iniciando carregamento do componente StoreProfile');
  if (!authStore.isStore) {
    console.log('onMounted: Usuário não é loja, redirecionando para /');
    router.push('/');
    return;
  }

  try {
    console.log('onMounted: Carregando perfil do usuário');
    loading.value = true;
    await authStore.fetchProfile();
    console.log('onMounted: Dados brutos do usuário:', authStore.user);
    if (authStore.user) {
      profile.value = {
        username: authStore.user.username || '',
        email: authStore.user.email || '',
        cnpj: authStore.user.cnpj || '',
        address: authStore.user.address || '',
        responsible: authStore.user.responsible || '',
        latitude: Number(authStore.user.latitude) || 0,
        longitude: Number(authStore.user.longitude) || 0,
        use_bulk_pricing: authStore.user.use_bulk_pricing || false,
        has_loyalty_card: authStore.user.has_loyalty_card || false,
      };
      console.log('onMounted: Perfil carregado:', profile.value);
      if (!profile.value.username) {
        console.warn('onMounted: Dados do perfil incompletos');
        error.value = 'Dados do perfil incompletos. Verifique as informações da loja.';
      }
    } else {
      console.error('onMounted: Usuário não encontrado');
      error.value = 'Usuário não encontrado';
    }
  } catch (err: any) {
    console.error('onMounted: Erro ao carregar perfil:', err);
    error.value = err.message || 'Erro ao carregar perfil';
  } finally {
    loading.value = false;
  }
});

function openDetailsModal() {
  console.log('openDetailsModal: Abrindo modal de detalhes');
  detailsModal.value = true;
}

function openEditModal(item) {
  console.log('openEditModal: Abrindo modal de edição com item:', item);
  editForm.value = { ...item };
  editModal.value = true;
}

function confirmDeleteProfile(item) {
  console.log('confirmDeleteProfile: Abrindo confirmação de exclusão para item:', item);
  editForm.value = { ...item };
  confirmDelete.value = true;
}

async function updateProfile() {
  console.log('updateProfile: Tentando atualizar perfil com dados:', editForm.value);
  try {
    loading.value = true;
    error.value = '';

    const formData = {
      ...editForm.value,
      latitude: Number(editForm.value.latitude),
      longitude: Number(editForm.value.longitude),
      use_bulk_pricing: editForm.value.use_bulk_pricing,
      has_loyalty_card: editForm.value.has_loyalty_card,
    };

    await authStore.updateProfile(formData);

    profile.value = { ...editForm.value };
    editModal.value = false;
    error.value = 'Perfil atualizado com sucesso!';
    console.log('updateProfile: Perfil atualizado com sucesso');
  } catch (err: any) {
    console.error('updateProfile: Erro ao atualizar perfil:', err);
    error.value = err.message || 'Erro ao atualizar perfil';
  } finally {
    loading.value = false;
  }
}

async function deleteProfile() {
  console.log('deleteProfile: Tentando excluir perfil');
  try {
    deleting.value = true;
    error.value = '';

    await authStore.deleteProfile();
    await router.push('/');
    console.log('deleteProfile: Perfil excluído com sucesso');
  } catch (err: any) {
    console.error('deleteProfile: Erro ao excluir perfil:', err);
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