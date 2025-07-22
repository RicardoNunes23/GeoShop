<template>
  <div class="d-flex align-center" :class="customClass">
    <!-- Botão de Visualização (Detalhes) -->
    <v-tooltip v-if="showDetails" bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          v-bind="attrs"
          :color="detailsColor"
          :small="small"
          class="mr-2"
          v-on="{ ...on, click: () => $emit('details', item) }" <!-- Combina eventos -->
        >
          <v-icon :small="small">mdi-eye</v-icon>
          <span v-if="!iconOnly" class="ml-2">Detalhes</span>
        </v-btn>
      </template>
      <span>Ver Detalhes</span>
    </v-tooltip>

    <!-- Botão de Edição -->
    <v-tooltip v-if="showEdit" bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          v-bind="attrs"
          :color="editColor"
          :small="small"
          class="mr-2"
          v-on="{ ...on, click: () => $emit('edit', item) }"
        >
          <v-icon :small="small">mdi-pencil</v-icon>
          <span v-if="!iconOnly" class="ml-2">Editar</span>
        </v-btn>
      </template>
      <span>Editar</span>
    </v-tooltip>

    <!-- Botão de Exclusão -->
    <v-tooltip v-if="showDelete" bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          v-bind="attrs"
          :color="deleteColor"
          :small="small"
          v-on="{ ...on, click: () => $emit('delete', item) }"
        >
          <v-icon :small="small">mdi-delete</v-icon>
          <span v-if="!iconOnly" class="ml-2">Excluir</span>
        </v-btn>
      </template>
      <span>Excluir</span>
    </v-tooltip>

    <!-- Slot para botões personalizados -->
    <slot name="custom-actions"></slot>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true,
  },
  showDetails: {
    type: Boolean,
    default: false,
  },
  showEdit: {
    type: Boolean,
    default: true,
  },
  showDelete: {
    type: Boolean,
    default: true,
  },
  detailsColor: {
    type: String,
    default: 'primary',
  },
  editColor: {
    type: String,
    default: 'warning',
  },
  deleteColor: {
    type: String,
    default: 'error',
  },
  small: {
    type: Boolean,
    default: true,
  },
  iconOnly: {
    type: Boolean,
    default: false,
  },
  customClass: {
    type: String,
    default: '',
  },
});

defineEmits(['details', 'edit', 'delete']);
</script>

<style scoped>
.d-flex {
  gap: 8px;
}

.v-btn {
  text-transform: none;
  letter-spacing: normal;
}
</style>