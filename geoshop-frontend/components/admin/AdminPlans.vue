<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col>
        <h1 class="text-h5 font-weight-bold mb-6">Gerenciar Planos</h1>
      </v-col>
    </v-row>

    <v-row v-if="planStore.loading">
      <v-col class="text-center">
        <v-progress-circular indeterminate color="primary" />
        <span class="ml-2">Carregando...</span>
      </v-col>
    </v-row>

    <v-alert v-if="planStore.error" type="error" class="mb-4" dismissible @input="planStore.error = null">
      {{ planStore.error }}
    </v-alert>

    <!-- Botão de criação visível apenas para admin -->
    <v-row v-if="authStore.isAdmin" class="mb-4">
      <v-col>
        <v-btn color="primary" @click="startCreating">Criar Novo Plano</v-btn>
      </v-col>
    </v-row>

    <!-- Tabela de planos -->
    <v-row>
      <v-col>
        <v-data-table
          :headers="filteredHeaders"
          :items="planStore.plans"
          class="elevation-1"
          :items-per-page="10"
        >
          <template v-slot:item.price="{ item }">
            R$ {{ item.price.toFixed(2) }}
          </template>
          
          <!-- Ações visíveis apenas para admin -->
          <template v-if="authStore.isAdmin" v-slot:item.actions="{ item }">
            <v-btn color="primary" small class="mr-2" @click="startEditing(item)">
              Editar
            </v-btn>
            <v-btn color="error" small @click="confirmDelete(item)">
              Excluir
            </v-btn>
          </template>
        </v-data-table>
      </v-col>
    </v-row>

    <!-- Diálogo de criação/edição -->
    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card>
        <v-card-title>{{ editingPlan ? 'Editar Plano' : 'Criar Plano' }}</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-select
              v-model="formData.name"
              :items="planOptions"
              label="Tipo de Plano"
              :rules="[v => !!v || 'Tipo é obrigatório']"
              required
            />
            <v-text-field
              v-model.number="formData.price"
              label="Preço (R$)"
              type="number"
              step="0.01"
              min="0"
              :rules="[v => !!v || 'Preço é obrigatório', v => v >= 0 || 'Preço inválido']"
              required
            />
            <v-text-field
              v-model.number="formData.product_limit"
              label="Limite de Produtos"
              type="number"
              min="0"
              :rules="[v => !!v || 'Limite é obrigatório', v => v >= 0 || 'Limite inválido']"
              required
            />
            <v-textarea
              v-model="formData.description"
              label="Descrição"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" text @click="cancel">Cancelar</v-btn>
          <v-btn color="primary" :loading="planStore.loading" @click="savePlan">
            {{ editingPlan ? 'Salvar' : 'Criar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title>Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o plano "{{ deletePlan?.get_name_display }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" text @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" :loading="planStore.loading" @click="deleteSelectedPlan">Excluir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlanStore } from '~/stores/plans'
import { useAuthStore } from '~/stores/auth'

const planStore = usePlanStore()
const authStore = useAuthStore()
const form = ref(null)
const dialog = ref(false)
const deleteDialog = ref(false)
const valid = ref(false)
const editingPlan = ref(null)
const deletePlan = ref(null)

const formData = ref({
  name: '',
  price: 0,
  product_limit: 0,
  description: ''
})

const planOptions = [
  { value: 'A', text: 'Plano A - Grátis' },
  { value: 'B', text: 'Plano B' },
  { value: 'C', text: 'Plano C' },
  { value: 'D', text: 'Plano D' },
  { value: 'E', text: 'Plano E' }
]

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Nome', key: 'get_name_display' },
  { title: 'Preço', key: 'price' },
  { title: 'Limite de Produtos', key: 'product_limit' },
  { title: 'Descrição', key: 'description' },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Filtra cabeçalhos para não mostrar ações se não for admin
const filteredHeaders = computed(() => {
  return authStore.isAdmin ? headers : headers.filter(h => h.key !== 'actions')
})

onMounted(() => {
  planStore.fetchPlans()
})

function startCreating() {
  editingPlan.value = null
  formData.value = { name: '', price: 0, product_limit: 0, description: '' }
  dialog.value = true
}

function startEditing(plan) {
  editingPlan.value = plan
  formData.value = { ...plan }
  dialog.value = true
}

async function savePlan() {
  const { valid } = await form.value.validate()
  if (!valid) return

  try {
    if (editingPlan.value) {
      await planStore.updatePlan(editingPlan.value.id, formData.value)
    } else {
      await planStore.savePlan(formData.value)
    }
    dialog.value = false
  } catch (error) {
    console.error('Erro ao salvar plano:', error)
  }
}

function confirmDelete(plan) {
  deletePlan.value = plan
  deleteDialog.value = true
}

async function deleteSelectedPlan() {
  try {
    await planStore.deletePlan(deletePlan.value.id)
    deleteDialog.value = false
  } catch (error) {
    console.error('Erro ao excluir plano:', error)
  }
}

function cancel() {
  dialog.value = false
  editingPlan.value = null
  form.value?.reset()
}
</script>