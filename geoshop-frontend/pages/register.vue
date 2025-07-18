<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row class="fill-height" no-gutters>
          <v-col cols="12" md="6" class="d-none d-md-flex">
            <v-img
              src="https://source.unsplash.com/random/800x600?city"
              cover
              class="fill-height"
              gradient="to top right, rgba(0,0,0,.1), rgba(0,0,0,.5)"
            >
              <div class="d-flex fill-height align-center justify-center">
                <h1 class="text-white text-h3 font-weight-bold px-8">
                  Bem-vindo ao GeoShop
                </h1>
              </div>
            </v-img>
          </v-col>

          <v-col cols="12" md="6" class="d-flex align-center justify-center">
            <v-card flat class="px-8 py-6" max-width="500">
              <v-card-title class="text-h4 font-weight-bold mb-6">
                Crie sua conta
              </v-card-title>

              <v-tabs v-model="activeTab" color="primary" grow>
                <v-tab value="client">Sou Cliente</v-tab>
                <v-tab value="store">Sou Loja</v-tab>
              </v-tabs>

              <v-card-text>
                <v-window v-model="activeTab">
                  <v-window-item value="client">
                    <v-form @submit.prevent="registerClient" class="mt-4">
                      <v-text-field
                        v-model="client.username"
                        label="Nome de usuário"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="client.email"
                        label="E-mail"
                        type="email"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="client.password"
                        label="Senha"
                        type="password"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-btn
                        type="submit"
                        color="primary"
                        block
                        size="large"
                        :loading="loading"
                      >
                        Registrar como Cliente
                      </v-btn>
                    </v-form>
                  </v-window-item>

                  <v-window-item value="store">
                    <v-form @submit.prevent="registerStore" class="mt-4">
                      <v-text-field
                        v-model="store.username"
                        label="Nome da Loja"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.email"
                        label="E-mail"
                        type="email"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.password"
                        label="Senha"
                        type="password"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.cnpj"
                        label="CNPJ"
                        v-mask="'##.###.###/####-##'"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.address"
                        label="Endereço"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.responsible"
                        label="Responsável"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-text-field
                        v-model="store.phone"
                        label="Telefone"
                        v-mask="'+55 (##) #####-####'"
                        required
                        class="mb-4"
                      ></v-text-field>

                      <v-row>
                        <v-col cols="6">
                          <v-text-field
                            v-model.number="store.latitude"
                            label="Latitude"
                            type="number"
                            step="0.000001"
                            :rules="[v => (v >= -90 && v <= 90) || 'Latitude deve estar entre -90 e 90']"
                            required
                          ></v-text-field>
                        </v-col>
                        <v-col cols="6">
                          <v-text-field
                            v-model.number="store.longitude"
                            label="Longitude"
                            type="number"
                            step="0.000001"
                            :rules="[v => (v >= -180 && v <= 180) || 'Longitude deve estar entre -180 e 180']"
                            required
                          ></v-text-field>
                        </v-col>
                      </v-row>

                      <v-checkbox
                        v-model="store.use_bulk_pricing"
                        label="Trabalhar com quantidade mínima?"
                        class="mt-2"
                      ></v-checkbox>

                      <v-checkbox
                        v-model="store.has_loyalty_card"
                        label="Oferecer cartão fidelidade?"
                        class="mt-2"
                      ></v-checkbox>

                      <v-btn
                        type="submit"
                        color="primary"
                        block
                        size="large"
                        :loading="loading"
                      >
                        Registrar como Loja
                      </v-btn>
                    </v-form>
                  </v-window-item>
                </v-window>

                <v-divider class="my-6"></v-divider>

                <div class="text-center">
                  <p class="text-body-2">
                    Já tem uma conta?
                    <router-link to="/login" class="text-primary font-weight-bold">
                      Faça login
                    </router-link>
                  </p>
                </div>

                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  class="mt-4"
                >
                  {{ error }}
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { useAuthStore } from '~/stores/auth';
import { usePlanStore } from '~/stores/plans';
import { useRouter } from 'vue-router';
import { mask } from 'vue-the-mask';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const planStore = usePlanStore();
const router = useRouter();

const activeTab = ref<'client' | 'store'>('client');
const loading = ref(false);
const error = ref('');

const client = reactive({
  username: '',
  email: '',
  password: ''
});

const store = reactive({
  username: '',
  email: '',
  password: '',
  cnpj: '',
  address: '',
  responsible: '',
  phone: '',
  latitude: 0,
  longitude: 0,
  use_bulk_pricing: false,
  has_loyalty_card: false,
  plan_id: 1 // Valor padrão para o plano gratuito (ajuste conforme o ID do backend)
});

onMounted(async () => {
  try {
    await planStore.fetchPlans();
    const freePlan = planStore.plans.find(plan => plan.price === 0);
    if (freePlan) {
      store.plan_id = freePlan.id;
    } else {
      console.warn('Plano gratuito não encontrado, usando ID padrão');
    }
  } catch (err) {
    console.error('Erro ao buscar planos:', err);
  }
});

async function registerClient() {
  try {
    loading.value = true;
    error.value = '';
    await authStore.registerClient(client.username, client.email, client.password);
    await router.push('/login');
  } catch (err: any) {
    error.value = err.message || 'Erro ao registrar cliente';
  } finally {
    loading.value = false;
  }
}

async function registerStore() {
  try {
    loading.value = true;
    error.value = '';
    
    const storeData = {
      username: store.username,
      email: store.email,
      password: store.password,
      cnpj: store.cnpj,
      address: store.address,
      responsible: store.responsible,
      phone: store.phone,
      latitude: Number(store.latitude),
      longitude: Number(store.longitude),
      use_bulk_pricing: store.use_bulk_pricing,
      has_loyalty_card: store.has_loyalty_card,
      plan_id: store.plan_id
    };
    
    await authStore.registerStore(storeData);
    await router.push('/login');
  } catch (err: any) {
    error.value = err.message || 'Erro ao registrar loja';
  } finally {
    loading.value = false;
  }
}

const vMask = mask;
</script>

<style scoped>
.fill-height {
  height: 100vh;
}

.v-tab {
  letter-spacing: normal;
  text-transform: none;
  font-weight: 500;
}
</style>