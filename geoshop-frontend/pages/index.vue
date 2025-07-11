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
             
        <v-btn to="/login" variant="text" class="text-secondary">Login</v-btn>
        <v-btn to="/register" variant="text" class="text-secondary">Registrar</v-btn>
             
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { useAuthStore } from '~/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

// Estado da aba ativa
const tab = ref<'login' | 'register'>('login')

// Estado do login
const username = ref('')
const password = ref('')
const remember = ref(false)
const error = ref('')
const loading = ref(false)

// Estado do registro
const register = reactive({
  name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  user_type: '',
  terms: false
})

const userTypes = [
  { title: 'Cliente', value: 'client' },
  { title: 'Loja', value: 'store' },
  
]

// Função de login adaptada
const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  try {
    await authStore.login(username.value, password.value)
    
    // Redirecionamento condicional
    switch(authStore.user?.user_type) {
      case 'client':
        await navigateTo('/clients')
        break
      case 'store':
        await navigateTo('/store')
        break
      case 'admin':
        await navigateTo('/admin')
        break
      default:
        await navigateTo('/')
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao fazer login'
  } finally {
    loading.value = false
  }
}

// Função de registro (exemplo)
const handleRegister = async () => {
  loading.value = true
  try {
    // Aqui você implementaria a lógica de registro
    console.log('Registrando:', register)
    // Simulando um registro bem-sucedido
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Após registrar, faz login automaticamente
    username.value = register.username
    password.value = register.password
    await handleLogin()
  } catch (err: any) {
    error.value = err.message || 'Erro ao registrar'
  } finally {
    loading.value = false
  }
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