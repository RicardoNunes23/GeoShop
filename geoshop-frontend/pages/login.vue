<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row class="fill-height" no-gutters>
          <!-- Coluna da imagem (esquerda) -->
          <v-col cols="12" md="6" class="d-none d-md-flex">
            <v-img
              src="https://source.unsplash.com/random/800x600?nature"
              cover
              class="fill-height"
              gradient="to top right, rgba(0,0,0,.1), rgba(0,0,0,.5)"
            >
              <div class="d-flex fill-height align-center justify-center">
                <h1 class="text-white text-h3 font-weight-bold px-8">
                  Bem-vindo ao Nosso Sistema
                </h1>
              </div>
            </v-img>
          </v-col>

          <!-- Coluna do formulário (direita) -->
          <v-col cols="12" md="6" class="d-flex align-center justify-center">
            <v-card flat class="px-8 py-6" max-width="500">
              <v-card-title class="text-h4 font-weight-bold mb-6">
                Acesse sua conta
              </v-card-title>

              <v-card-text>
                <v-form @submit.prevent="handleLogin">
                  <v-text-field
                    v-model="username"
                    label="Nome de Usuário"
                    required
                    class="mb-4"
                  ></v-text-field>

                  <v-text-field
                    v-model="password"
                    label="Senha"
                    type="password"
                    required
                    class="mb-4"
                  ></v-text-field>

                  <div class="d-flex justify-space-between align-center mb-4">
                    <v-checkbox
                      v-model="remember"
                      label="Lembrar-me"
                    ></v-checkbox>

                    <a href="#" class="text-primary">Esqueceu a senha?</a>
                  </div>

                  <v-btn
                    type="submit"
                    color="primary"
                    block
                    size="large"
                    class="mb-4"
                    :loading="loading"
                  >
                    Entrar
                  </v-btn>

                  <v-alert
                    v-if="error"
                    type="error"
                    variant="tonal"
                    class="mb-4"
                  >
                    {{ error }}
                  </v-alert>
                </v-form>

                <div class="text-center mt-4">
                  <p class="text-body-2">
                    Não tem uma conta?
                    <a 
                      href="/register" 
                      class="text-primary font-weight-bold"
                      @click.prevent="navigateToRegister"
                    >
                      Cadastre-se
                    </a>
                  </p>
                </div>

                <v-divider class="my-6"></v-divider>

                <div class="text-center">
                  <p class="text-body-2 mb-2">Ou entre com</p>
                  <div class="d-flex justify-center gap-4">
                    <v-btn icon variant="outlined">
                      <v-icon>mdi-google</v-icon>
                    </v-btn>
                    <v-btn icon variant="outlined">
                      <v-icon>mdi-facebook</v-icon>
                    </v-btn>
                    <v-btn icon variant="outlined">
                      <v-icon>mdi-twitter</v-icon>
                    </v-btn>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: 'auth', // Usa o layout sem sidebar
 
});

const authStore = useAuthStore()

// Estado do login
const username = ref('')
const password = ref('')
const remember = ref(false)
const error = ref('')
const loading = ref(false)

// Função de login adaptada
const handleLogin = async () => {
  error.value = '';
  loading.value = true;

  try {
    await authStore.login(username.value, password.value);
   

    switch (authStore.user?.user_type) {
      case 'client':
        await navigateTo('/clients');
        break;
      case 'store':
        await navigateTo('/store?view=profile');
        break;
      case 'admin':
        await navigateTo('/admin?view=profile');
        break;
      default:
        await navigateTo('/');
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao fazer login';
  } finally {
    loading.value = false;
  }
};

// Navegação para a página de registro
const navigateToRegister = () => {
  navigateTo('/register')
}
</script>

<style scoped>
.fill-height {
  height: 100vh;
}

.gap-4 {
  gap: 16px;
}
</style>