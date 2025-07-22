<!-- components/app/BestStoreResult.vue -->
<template>
  <v-card>
    <v-card-title class="text-h5 font-weight-bold text-primary">
      Melhor Loja Encontrada
    </v-card-title>
    <v-card-text>
      <v-alert
        v-if="!bestStore"
        type="warning"
        variant="tonal"
      >
        Nenhuma loja encontrada para os itens selecionados.
      </v-alert>
      <div v-else>
        <p><strong>Loja:</strong> {{ bestStore.username }}</p>
        <p><strong>Preço Total:</strong> R$ {{ bestStore.total_price.toFixed(2) }}</p>
        <p><strong>Número de Itens:</strong> {{ bestStore.items_count }}</p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="grey" @click="$emit('close')">Fechar</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
defineProps({
  bestStore: {
    type: Object,
    default: null,
  },
});

defineEmits(['close']);
</script>

<style scoped>
.v-btn {
  text-transform: none;
  letter-spacing: normal;
}
</style>