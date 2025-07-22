<template>
  <div>
    <h2 class="text-h4 font-weight-bold text-primary mb-6">
      Perfil da Loja
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
        <template v-slot:item.use_bulk_pricing="{ item }">
          {{ item.use_bulk_pricing ? 'Sim' : 'Não' }}
        </template>
        <template v-slot:item.has_loyalty_card="{ item }">
          {{ item.has_loyalty_card ? 'Sim' : 'Não' }}
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
                <p><strong>Telefone:</strong> {{ formatPhone(profile.phone) || 'Não informado' }}</p>
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
                v-model="editForm.phone"
                label="Telefone"
                prepend-inner-icon="mdi-phone"
                v-mask="'+55 (##) #####-####'"
                outlined
                :rules="[v => !!v || 'Telefone é obrigatório', v => /^\+55 \(\d{2}\) \d{5}-\d{4}$/.test(v) || 'Telefone inválido']"
              />
              <v-text-field
                v-model="editForm.cnpj"
                label="CNPJ"
                prepend-inner-icon="mdi-file-document"
                v-mask="'##.###.###/####-##'"
                outlined
                :rules="[
                  v => !!v || 'CNPJ é obrigatório',
                  v => /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(v) || 'CNPJ inválido',
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
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';
import { mask } from 'vue-the-mask';
import AppDataTable from '~/components/app/AppDataTable.vue';

const authStore = useAuthStore();
const router = useRouter();

const profileKey = ref(0); // Chave para forçar re-renderização
const profile = computed(() => {
 
  return {
    username: authStore.user?.username || '',
    email: authStore.user?.email || '',
    phone: authStore.user?.phone || '',
    cnpj: authStore.user?.cnpj || '',
    address: authStore.user?.address || '',
    responsible: authStore.user?.responsible || '',
    latitude: Number(authStore.user?.latitude) || 0,
    longitude: Number(authStore.user?.longitude) || 0,
    use_bulk_pricing: authStore.user?.use_bulk_pricing || false,
    has_loyalty_card: authStore.user?.has_loyalty_card || false,
    ...authStore.user
  };
});

const headers = ref([
  { title: 'Nome', key: 'username', sortable: true },
  { title: 'Responsável', key: 'responsible', sortable: true },
  { title: 'E-mail', key: 'email', sortable: true },
  { title: 'Telefone', key: 'phone', sortable: true },
  { title: 'Trabalha com Qtd. Mínima', key: 'use_bulk_pricing', sortable: true },
  { title: 'Tem Cartão Fidelidade', key: 'has_loyalty_card', sortable: true },
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
  phone: '',
  cnpj: '',
  address: '',
  responsible: '',
  latitude: 0,
  longitude: 0,
  use_bulk_pricing: false,
  has_loyalty_card: false
});

const editFormValid = computed(() => {
  return (
    !!editForm.value.username &&
    !!editForm.value.email &&
    /.+@.+\..+/.test(editForm.value.email) &&
    !!editForm.value.phone &&
    /^\+55 \(\d{2}\) \d{5}-\d{4}$/.test(editForm.value.phone) &&
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
        username: newUser.username || '',
        email: newUser.email || '',
        phone: formatPhone(newUser.phone) || '',
        cnpj: newUser.cnpj || '',
        address: newUser.address || '',
        responsible: newUser.responsible || '',
        latitude: Number(newUser.latitude) || 0,
        longitude: Number(newUser.longitude) || 0,
        use_bulk_pricing: newUser.use_bulk_pricing || false,
        has_loyalty_card: newUser.has_loyalty_card || false
      };
     
    }
  },
  { immediate: true, deep: true }
);

onMounted(async () => {
  if (!authStore.isStore) {
    router.push('/');
    return;
  }

  try {
    loading.value = true;
    await authStore.fetchProfile();
  } catch (err: any) {
    console.error('onMounted: Erro ao carregar perfil:', err);
    error.value = err.message || 'Erro ao carregar perfil';
  } finally {
    loading.value = false;
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

    // Remove a formatação do telefone antes de enviar ao backend
    const cleanPhone = editForm.value.phone.replace(/\D/g, '');
    const formData = {
      username: editForm.value.username,
      email: editForm.value.email,
      phone: cleanPhone,
      cnpj: editForm.value.cnpj,
      address: editForm.value.address,
      responsible: editForm.value.responsible,
      latitude: Number(editForm.value.latitude),
      longitude: Number(editForm.value.longitude),
      use_bulk_pricing: editForm.value.use_bulk_pricing,
      has_loyalty_card: editForm.value.has_loyalty_card
    };
 

    await authStore.updateProfile(formData);
    await authStore.fetchProfile(); // Força a atualização do estado com os dados mais recentes do backend

    editModal.value = false;
    error.value = 'Perfil atualizado com sucesso!';
    profileKey.value++; // Força re-renderização da tabela
  } catch (err: any) {
    console.error('updateProfile: Erro ao atualizar perfil:', err);
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