<!-- pages/plans.vue -->
<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col>
        <h1 class="text-h5 font-weight-bold mb-6">Gerenciar Planos</h1>
      </v-col>
    </v-row>

    <v-alert
      v-if="planStore.error"
      type="error"
      class="mb-4"
      dismissible
      @input="planStore.error = null"
    >
      {{ planStore.error }}
    </v-alert>

    <!-- Botão de criação visível apenas para admin -->
    <v-row v-if="authStore.isAdmin" class="mb-4">
      <v-col>
        <v-btn color="primary" @click="startCreating">
          <v-icon left>mdi-plus</v-icon>
          Criar Novo Plano
        </v-btn>
      </v-col>
    </v-row>

    <!-- Tabela de planos -->
    <AppDataTable
      :headers="filteredHeaders"
      :items="planStore.plans"
      :loading="planStore.loading"
      :items-per-page="10"
      :hide-actions="!authStore.isAdmin"
    >
      <template v-slot:item.price="{ item }">
        R$ {{ item.price.toFixed(2) }}
      </template>
      <template v-slot:item.ativo="{ item }">
        <v-chip :color="item.ativo ? 'success' : 'error'" small>
          {{ item.ativo ? 'Ativo' : 'Inativo' }}
        </v-chip>
      </template>
      <template v-if="authStore.isAdmin" v-slot:actions="{ item }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              color="primary"
              small
              class="mr-2"
              @click="startEditing(item)"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
          </template>
          <span>Editar</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              color="error"
              small
              @click="confirmDelete(item)"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
          <span>Excluir</span>
        </v-tooltip>
      </template>
    </AppDataTable>

    <!-- Diálogo de criação/edição -->
    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ editingPlan ? 'Editar Plano' : 'Criar Plano' }}</span>
          <v-switch
            v-model="formData.ativo"
            label="Plano Ativo"
            color="success"
            hide-details
            class="mt-0"
          />
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="formData.name"
              label="Nome do Plano"
              :rules="[v => !!v || 'Nome é obrigatório']"
              required
              outlined
              class="mb-4"
            />
            <v-text-field
              v-model="formData.price"
              label="Preço (R$)"
              type="number"
              step="0.01"
              min="0"
              :rules="[
                v => (v !== null && v !== '' && v !== undefined) || 'Preço é obrigatório',
                v => Number(v) >= 0 || 'Preço não pode ser negativo',
                v => /^\d+(\.\d{1,2})?$/.test(v) || 'Formato inválido (use 00.00)'
              ]"
              required
              outlined
              class="mb-4"
              @blur="formatPrice"
            />
            <v-text-field
              v-model.number="formData.product_limit"
              label="Limite de Produtos"
              type="number"
              min="0"
              :rules="[v => !!v || 'Limite é obrigatório', v => v >= 0 || 'Limite deve ser positivo']"
              required
              outlined
              class="mb-4"
            />
            <v-textarea
              v-model="formData.description"
              label="Descrição"
              rows="3"
              outlined
              counter="500"
              :rules="[v => !v || v.length <= 500 || 'Máximo 500 caracteres']"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" text @click="cancel">Cancelar</v-btn>
          <v-btn
            color="primary"
            :loading="planStore.loading"
            @click="savePlan"
            :disabled="!valid"
          >
            {{ editingPlan ? 'Salvar Alterações' : 'Criar Plano' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="headline">Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o plano <strong>"{{ deletePlan?.name }}"</strong>?
          <v-alert
            v-if="deletePlan?.users_count > 0"
            type="warning"
            class="mt-3"
          >
            Este plano está associado a {{ deletePlan?.users_count }} usuário(s). A exclusão afetará esses usuários.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" text @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn
            color="error"
            :loading="planStore.loading"
            @click="deleteSelectedPlan"
          >
            Confirmar Exclusão
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { usePlanStore } from '~/stores/plans';
import { useAuthStore } from '~/stores/auth';
import AppDataTable from '~/components/AppDataTable.vue';

const planStore = usePlanStore();
const authStore = useAuthStore();
const form = ref(null);
const dialog = ref(false);
const deleteDialog = ref(false);
const valid = ref(false);
const editingPlan = ref(null);
const deletePlan = ref(null);

const formData = ref({
  name: '',
  price: 0,
  product_limit: 0,
  description: '',
  ativo: true,
});

const headers = [
  { title: 'ID', key: 'id', width: '80px' },
  { title: 'Nome', key: 'name' },
  { title: 'Preço', key: 'price', align: 'end' },
  { title: 'Limite', key: 'product_limit', align: 'end' },
  { title: 'Status', key: 'ativo', align: 'center' },
  { title: 'Ações', key: 'actions', sortable: false, align: 'center', width: '120px' },
];

const filteredHeaders = computed(() => {
  return authStore.isAdmin ? headers : headers.filter((h) => h.key !== 'actions');
});

onMounted(() => {
  planStore.fetchPlans();
});

function formatPrice() {
  if (formData.value.price === '' || formData.value.price === null) {
    formData.value.price = 0;
  } else {
    formData.value.price = parseFloat(formData.value.price).toFixed(2);
  }
}

function startCreating() {
  editingPlan.value = null;
  formData.value = {
    name: '',
    price: 0,
    product_limit: 0,
    description: '',
    ativo: true,
  };
  dialog.value = true;
}

function startEditing(plan) {
  editingPlan.value = plan;
  formData.value = {
    name: plan.name,
    price: plan.price,
    product_limit: plan.product_limit,
    description: plan.description,
    ativo: plan.ativo,
  };
  dialog.value = true;
}

async function savePlan() {
  const { valid } = await form.value.validate();
  if (!valid) return;

  try {
    if (editingPlan.value) {
      await planStore.updatePlan(editingPlan.value.id, formData.value);
    } else {
      await planStore.savePlan(formData.value);
    }
    dialog.value = false;
  } catch (error) {
    console.error('Erro ao salvar plano:', error);
  }
}

function confirmDelete(plan) {
  deletePlan.value = {
    ...plan,
    users_count: plan.users?.length || 0,
  };
  deleteDialog.value = true;
}

async function deleteSelectedPlan() {
  try {
    await planStore.deletePlan(deletePlan.value.id);
    deleteDialog.value = false;
  } catch (error) {
    console.error('Erro ao excluir plano:', error);
  }
}

function cancel() {
  dialog.value = false;
  editingPlan.value = null;
  form.value?.reset();
}
</script>

<style scoped>
.v-data-table >>> .v-data-table-header th {
  font-weight: bold;
  background-color: #f5f5f5;
}
</style>