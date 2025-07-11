<template>
  <div>
    <h2 class="text-h4 font-weight-bold text-primary mb-6">
      Perfil da Loja
    </h2>
    
    <!-- Tabela sem bordas -->
    <div class="pa-4 mb-6">
      <v-data-table
        :items="[profile]"
        :headers="headers"
        hide-default-footer
        class="no-border"
      >
        <template v-slot:item.actions="{ item }">
          <div class="d-flex">
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
      </v-data-table>
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

    <!-- Modal de edição sem bordas -->
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
                :rules="[v => !!v || 'E-mail é obrigatório', v => /.+@.+\..+/.test(v) || 'E-mail inválido']" 
              />
              <v-text-field 
                v-model="editForm.cnpj" 
                label="CNPJ"
                prepend-inner-icon="mdi-file-document" 
                v-mask="'##.###.###/####-##'" 
                outlined
                :rules="[v => !!v || 'CNPJ é obrigatório', v => /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(v) || 'CNPJ inválido']" 
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
            </v-col>
          </v-row>
          
          <div class="justify-end mt-4 d-flex">
            <v-btn 
              color="grey" 
              @click="editModal = false"
            >
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

    <!-- Modal de confirmação de exclusão sem bordas -->
    <v-dialog v-model="confirmDelete" max-width="500" persistent>
      <div class="modal-content">
        <h2 class="text-h5 font-weight-bold text-primary">
          Confirmar Exclusão
        </h2>
        <p>
          Tem certeza que deseja excluir sua conta permanentemente? Esta ação não pode ser desfeita.
        </p>
        <div class="d-flex justify-end">
          <v-btn text @click="confirmDelete = false">Cancelar</v-btn>
          <v-btn color="error" @click="deleteProfile" :loading="deleting">
            ConfirmPurchase
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
});

const headers = ref([
  { title: 'Nome da Loja', key: 'username' },
  { title: 'E-mail', key: 'email' },
  { title: 'CNPJ', key: 'cnpj' },
  { title: 'Endereço', key: 'address' },
  { title: 'Responsável', key: 'responsible' },
  { title: 'Latitude', key: 'latitude' },
  { title: 'Longitude', key: 'longitude' },
  { title: 'Ações', key: 'actions', sortable: false },
]);

const editModal = ref(false);
const editForm = ref({
  username: '',
  email: '',
  cnpj: '',
  address: '',
  responsible: '',
  latitude: 0,
  longitude: 0,
});

const loading = ref(false);
const deleting = ref(false);
const confirmDelete = ref(false);
const error = ref('');

const vMask = { mounted: mask };

const editFormValid = computed(() => {
  return (
    !!editForm.value.username &&
    !!editForm.value.email &&
    /.+@.+\..+/.test(editForm.value.email) &&
    !!editForm.value.cnpj &&
    /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(editForm.value.cnpj) &&
    !!editForm.value.address &&
    !!editForm.value.responsible &&
    editForm.value.latitude >= -90 && editForm.value.latitude <= 90 &&
    editForm.value.longitude >= -180 && editForm.value.longitude <= 180
  );
});

onMounted(async () => {
  // Verifica se o usuário é uma loja
  if (!authStore.isStore) {
    router.push('/');
    return;
  }

  try {
    // Usa o método genérico fetchProfile()
    await authStore.fetchProfile();
    
    if (authStore.user) {
      profile.value = {
        username: authStore.user.username || '',
        email: authStore.user.email || '',
        cnpj: authStore.user.cnpj || '',
        address: authStore.user.address || '',
        responsible: authStore.user.responsible || '',
        latitude: authStore.user.latitude || 0,
        longitude: authStore.user.longitude || 0,
      };
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar perfil';
  }
});

function openEditModal(item) {
  editForm.value = { ...item };
  editModal.value = true;
}

function confirmDeleteProfile(item) {
  confirmDelete.value = true;
}

async function updateProfile() {
  try {
    loading.value = true;
    error.value = '';

    const formData = {
      ...editForm.value,
      latitude: Number(editForm.value.latitude),
      longitude: Number(editForm.value.longitude),
    };

    // Usa o método genérico updateProfile()
    await authStore.updateProfile(formData);
    
    // Atualiza os dados locais
    profile.value = { ...editForm.value };
    editModal.value = false;
    error.value = 'Perfil atualizado com sucesso!';
  } catch (err: any) {
    error.value = err.message || 'Erro ao atualizar perfil';
  } finally {
    loading.value = false;
  }
}

async function deleteProfile() {
  try {
    deleting.value = true;
    error.value = '';
    
    // Usa o método genérico deleteProfile()
    await authStore.deleteProfile();
    
    await router.push('/');
  } catch (err: any) {
    error.value = err.message || 'Erro ao excluir conta';
  } finally {
    deleting.value = false;
    confirmDelete.value = false;
  }
}
</script>
<style scoped>
/* Estilos para remover bordas e ajustar aparência */
.no-border {
  border: none !important;
  box-shadow: none !important;
}

.modal-content {
  padding: 16px;
  background: white;
}

.v-data-table {
  width: 100%;
  border: none !important;
  box-shadow: none !important;
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
  
  .v-data-table {
    font-size: 0.8rem;
  }
  
  .v-btn {
    min-width: 36px !important;
    padding: 0 8px !important;
  }
}
</style>