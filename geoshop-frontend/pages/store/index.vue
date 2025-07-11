<template>
  <div>
    Tela Loja
  </div>
</template>

<script setup>
import { useState } from '#app';

definePageMeta({
  layout: 'sidebar',
  middleware: ['auth'], 
});

// Define os itens da sidebar usando useState
useState('sidebarItems', () => [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', route: '/dashboard' },
  { title: 'Produtos', icon: 'mdi-cart', route: '/products' },
  { title: 'Pedidos', icon: 'mdi-clipboard-list', route: '/orders' },
  { title: 'Listas', icon: 'mdi-plus', route: '/orders' },
  { title: 'Configurações', icon: 'mdi-cog', route: '/settings' },
]);
</script>

<style lang="scss" scoped>
</style>