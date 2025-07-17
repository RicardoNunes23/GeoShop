import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';

interface Plan {
  id: number;
  name: string;
  price: number;
  product_limit: number;
  description: string;
}

interface Subscription {
  id: number;
  plan: Plan;
  is_active: boolean;
  payment_status: string;
  created_at: string;
  updated_at: string;
}

export const usePlanStore = defineStore('plans', () => {
  const plans = ref<Plan[]>([]);
  const subscriptions = ref<Subscription[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const apiBase = useRuntimeConfig().public.apiBase;

  async function fetchPlans() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      console.log('Token usado na requisição:', authStore.token);
      const response = await $fetch(`${apiBase}/plans/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      plans.value = (response as Plan[]).map(plan => ({
        ...plan,
        price: parseFloat(plan.price as any),
        product_limit: parseInt(plan.product_limit as any, 10),
      }));
      console.log('Planos após conversão:', plans.value);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar planos';
      console.error('Erro ao buscar planos:', err);
    } finally {
      loading.value = false;
      console.log('Estado de loading após fetchPlans:', loading.value);
    }
  }

  async function fetchSubscriptions() {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token || !authStore.isStore) {
        throw new Error('Não autorizado');
      }
      const response = await $fetch(`${apiBase}/store/subscription/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      subscriptions.value = response as Subscription[];
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao buscar assinaturas';
      console.error('Erro ao buscar assinaturas:', err);
    } finally {
      loading.value = false;
    }
  }

  async function createSubscription(planId: number) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token || !authStore.isStore) {
        throw new Error('Não autorizado');
      }
      const response = await $fetch(`${apiBase}/store/subscription/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
        body: { plan_id: planId },
      });
      subscriptions.value.push(response as Subscription);
      await authStore.fetchProfile();
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao criar assinatura';
      console.error('Erro ao criar assinatura:', err);
    } finally {
      loading.value = false;
    }
  }

  async function savePlan(planData: Plan) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      if (!authStore.isAdmin) {
        throw new Error('Apenas administradores podem criar planos');
      }
      const response = await $fetch(`${apiBase}/plans/`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: planData,
      });
      plans.value.push({
        ...response,
        price: parseFloat(response.price as any),
        product_limit: parseInt(response.product_limit as any, 10),
      });
      console.log('Plano criado:', response);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao salvar plano';
      console.error('Erro ao salvar plano:', err);
    } finally {
      loading.value = false;
    }
  }

  async function updatePlan(planId: number, planData: Plan) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      if (!authStore.isAdmin) {
        throw new Error('Apenas administradores podem atualizar planos');
      }
      const response = await $fetch(`${apiBase}/plans/${planId}/`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          'Content-Type': 'application/json',
        },
        body: planData,
      });
      const updatedPlan = {
        ...response,
        price: parseFloat(response.price as any),
        product_limit: parseInt(response.product_limit as any, 10),
      };
      const index = plans.value.findIndex(plan => plan.id === planId);
      if (index !== -1) {
        plans.value[index] = updatedPlan;
      }
      console.log('Plano atualizado:', response);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao atualizar plano';
      console.error('Erro ao atualizar plano:', err);
    } finally {
      loading.value = false;
    }
  }

  async function deletePlan(planId: number) {
    loading.value = true;
    error.value = null;
    try {
      const authStore = useAuthStore();
      if (!authStore.token) {
        throw new Error('Token de autenticação não encontrado');
      }
      if (!authStore.isAdmin) {
        throw new Error('Apenas administradores podem excluir planos');
      }
      await $fetch(`${apiBase}/plans/${planId}/`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authStore.token}`,
        },
      });
      plans.value = plans.value.filter(plan => plan.id !== planId);
      console.log('Plano excluído:', planId);
    } catch (err: any) {
      error.value = err.data?.detail || 'Erro ao excluir plano';
      console.error('Erro ao excluir plano:', err);
    } finally {
      loading.value = false;
    }
  }

  return {
    plans,
    subscriptions,
    loading,
    error,
    fetchPlans,
    fetchSubscriptions,
    createSubscription,
    savePlan,
    updatePlan,
    deletePlan,
  };
});