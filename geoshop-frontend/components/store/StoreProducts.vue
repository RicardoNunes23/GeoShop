<template>
    <v-container>
        <h1>Gerenciamento de Produtos da Loja</h1>
        <v-btn color="primary" @click="openCreateDialog">Adicionar Produto</v-btn>
        <v-text-field v-model="tableSearch" label="Pesquisar" prepend-inner-icon="mdi-magnify" clearable class="mb-4" />
        <v-data-table :headers="filteredHeaders" :items="storeProductStore.storeProducts" :search="tableSearch"
            :loading="storeProductStore.loading" class="elevation-1 mt-4">

            <template v-slot:item.product.image="{ item }">
                <div>
                    <v-img :src="imageUrl(item.product?.image)" max-width="50" max-height="50"
                        @error="onImageError(item)" @click="openImageDialog(item)" style="cursor: pointer;"></v-img>
                </div>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn color="warning" small @click="openEditDialog(item)">Editar</v-btn>
                <v-btn color="error" small @click="confirmDelete(item.id)">Excluir</v-btn>
            </template>
        </v-data-table>

        <!-- Diálogo para adicionar/editar produto -->
        <v-dialog v-model="dialog" max-width="600px">
            <v-card>
                <v-card-title>
                    {{ isEditing ? 'Editar Produto da Loja' : 'Adicionar Produto da Loja' }}
                </v-card-title>
                <v-card-text>
                    <v-form v-model="valid" ref="form">
                        <v-autocomplete v-model="formData.product_id" :items="storeProductStore.products"
                            item-value="id" item-title="name" label="Produto"
                            :rules="[v => !!v || 'Produto é obrigatório']" required clearable return-object
                            auto-select-first>
                            <!-- Item na lista -->
                            <template v-slot:item="{ props, item }">
                                <v-list-item v-bind="props" :title="null">
                                    <template v-slot:prepend>
                                        <v-img :src="imageUrl(item.raw.image)" width="40" height="40" class="mr-2" cover></v-img>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">
                                        {{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit }}
                                    </v-list-item-title>
                                    <v-list-item-subtitle>
                                        <span class="d-block">Peso: 
                                            {{ item.raw.quantity }} {{ item.raw.weight_unit }}</span>
                                        <span v-if="item.raw.package_type" class="d-block">Embalagem: 
                                            {{ item.raw.package_type }}</span>
                                    </v-list-item-subtitle>
                                </v-list-item>
                            </template>

                            <!-- Item selecionado -->
                            <template v-slot:selection="{ item }">
                                <div class="d-flex align-center">
                                    <v-img :src="imageUrl(item.raw.image)" width="30" height="30" class="mr-2"
                                        cover></v-img>
                                    <span>{{ item.raw.name }} - {{ item.raw.quantity }} {{ item.raw.weight_unit}}</span>
                                </div>
                            </template>
                        </v-autocomplete>

                        <v-text-field v-model.number="formData.price" label="Preço" type="number" step="0.01"
                            :rules="[v => v > 0 || 'Preço deve ser maior que zero']" required></v-text-field>
                        
                        <!-- Campos condicionais para quantidade mínima -->
                        <template v-if="storeProfile?.use_bulk_pricing">
                            <v-text-field v-model.number="formData.bulk_price" label="Preço por Quantidade"
                                type="number" step="0.01"
                                :rules="[v => v === null || v >= 0 || 'Preço por quantidade não pode ser negativo']">
                            </v-text-field>
                            <v-text-field v-model.number="formData.bulk_min_quantity"
                                label="Quantidade Mínima" type="number"
                                :rules="[v => v === null || v >= 0 || 'Quantidade mínima não pode ser negativa']">
                            </v-text-field>
                        </template>

                        <!-- Campo condicional para fidelidade -->
                        <template v-if="storeProfile?.has_loyalty_card">
                            <v-text-field v-model.number="formData.loyalty_price" label="Preço por Fidelidade"
                                type="number" step="0.01"
                                :rules="[v => v === null || v >= 0 || 'Preço por fidelidade não pode ser negativo']">
                            </v-text-field>
                        </template>

                        <v-checkbox v-model="formData.is_active" label="Ativo"></v-checkbox>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="secondary" @click="dialog = false">Cancelar</v-btn>
                    <v-btn color="primary" @click="saveProduct" :disabled="!valid">Salvar</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Diálogo para visualizar imagem e detalhes -->
        <v-dialog v-model="imageDialog" max-width="600px">
            <v-card>
                <v-card-title>Detalhes do Produto</v-card-title>
                <v-card-text>
                    <v-img :src="imageUrl(selectedProduct?.product?.image)" max-height="300" contain
                        class="mb-4"></v-img>
                    <v-row>
                        <v-col cols="12">
                            <p><strong>Nome:</strong> {{ selectedProduct?.product?.name || 'N/A' }}</p>
                            <p><strong>Marca:</strong> {{ selectedProduct?.product?.brand || 'N/A' }}</p>
                            <p><strong>Tipo de Embalagem:</strong> {{ selectedProduct?.product?.package_type || 'N/A' }}
                            </p>
                            <p><strong>Quantidade:</strong> {{ selectedProduct?.product?.quantity || 'N/A' }}</p>
                            <p><strong>Unidade de Peso:</strong> {{ selectedProduct?.product?.weight_unit || 'N/A' }}
                            </p>
                            <p><strong>Descrição:</strong> {{ selectedProduct?.product?.description || 'Sem descrição'
                                }}</p>
                            <p><strong>Preço:</strong> {{ selectedProduct?.price || 'N/A' }}</p>
                            <p v-if="storeProfile?.use_bulk_pricing"><strong>Preço por Quantidade:</strong> {{ selectedProduct?.bulk_price || 'N/A' }}</p>
                            <p v-if="storeProfile?.use_bulk_pricing"><strong>Quantidade Mínima:</strong> {{ selectedProduct?.bulk_min_quantity || 'N/A' }}</p>
                            <p v-if="storeProfile?.has_loyalty_card"><strong>Preço por Fidelidade:</strong> {{ selectedProduct?.loyalty_price || 'N/A' }}</p>
                            <p><strong>Ativo:</strong> {{ selectedProduct?.is_active ? 'Sim' : 'Não' }}</p>
                        </v-col>
                    </v-row>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="secondary" @click="imageDialog = false">Fechar</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Diálogo de confirmação de exclusão -->
        <v-dialog v-model="deleteDialog" max-width="400px">
            <v-card>
                <v-card-title>Confirmar Exclusão</v-card-title>
                <v-card-text>Deseja realmente excluir este produto da loja?</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="secondary" @click="deleteDialog = false">Cancelar</v-btn>
                    <v-btn color="error" @click="deleteProduct">Excluir</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
            {{ snackbarText }}
            <template v-slot:action="{ attrs }">
                <v-btn text v-bind="attrs" @click="snackbar = false">Fechar</v-btn>
            </template>
        </v-snackbar>
    </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStoreProductStore } from '~/stores/storeProducts';
import { useAuthStore } from '~/stores/auth';
import { useRouter } from 'vue-router';

interface Product {
    id: number;
    name: string;
    brand: string;
    package_type: string;
    quantity: string;
    weight_unit: string;
    description?: string;
    image?: string;
}

interface StoreProduct {
    id: number;
    product_id: number;
    product: Product;
    price: number;
    bulk_price: number | null;
    bulk_min_quantity: number | null;
    loyalty_price: number | null;
    is_active: boolean;
}

definePageMeta({
    middleware: ['auth'],
});

const storeProductStore = useStoreProductStore();
const authStore = useAuthStore();
const dialog = ref(false);
const deleteDialog = ref(false);
const imageDialog = ref(false);
const isEditing = ref(false);
const valid = ref(false);
const deleteId = ref<number | null>(null);
const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('success');
const router = useRouter();
const selectedProduct = ref<Partial<StoreProduct> & { product?: Partial<Product> }>({});
const tableSearch = ref('');
const storeProfile = ref<any>(null);

const baseUrl = ref('http://localhost:8000');

const imageUrl = computed(() => {
    return (image: string | undefined) => {
        if (!image) return '/placeholder.png';
        if (image.startsWith('http://') || image.startsWith('https://')) {
            return image;
        }
        const cleanImagePath = image.startsWith('/') ? image.slice(1) : image;
        return `${baseUrl.value}/media/${cleanImagePath}`;
    };
});

// Filtra os headers com base nas configurações da loja
const filteredHeaders = computed(() => {
    return headers.filter(header => {
        if (header.key === 'bulk_price' || header.key === 'bulk_min_quantity') {
            return storeProfile.value?.use_bulk_pricing;
        }
        if (header.key === 'loyalty_price') {
            return storeProfile.value?.has_loyalty_card;
        }
        return true;
    });
});

const formData = ref({
    id: null as number | null,
    product_id: null as number | null,
    price: 0,
    bulk_price: null as number | null,
    bulk_min_quantity: null as number | null,
    loyalty_price: null as number | null,
    is_active: true,
});

const headers = [
    { title: 'Imagem', key: 'product.image', sortable: false },
    { title: 'Produto', key: 'product.name' },
    { title: 'Marca', key: 'product.brand' },
    { title: 'Peso', key: 'product.quantity', value: item => `${item.product?.quantity} ${item.product?.weight_unit}` },
    { title: 'Preço', key: 'price' },
    { title: 'Preço por Quantidade', key: 'bulk_price' },
    { title: 'Quantidade Mínima', key: 'bulk_min_quantity' },
    { title: 'Preço por Fidelidade', key: 'loyalty_price' },
    { title: 'Ativo', key: 'is_active' },
    { title: 'Ações', key: 'actions', sortable: false },
];

onMounted(async () => {
    // Carrega o perfil da loja
    if (authStore.isStore) {
        await authStore.fetchProfile();
        storeProfile.value = authStore.user;
    }
    
    storeProductStore.fetchStoreProducts();
    storeProductStore.fetchProducts();
});

function customProductFilter(item: any, queryText: string): boolean {
    if (!item || !queryText) return true;

    const normalizedQuery = queryText.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, '');

    const combinedFields = [
        item.name,
        item.brand,
        item.quantity,
        item.weight_unit,
    ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, '');

    return combinedFields.includes(normalizedQuery);
}

function onImageError(item: any) {
    console.error(`Erro ao carregar imagem para o produto ${item.product?.name}: ${item.product?.image}`);
}

function openImageDialog(item: StoreProduct) {
    selectedProduct.value = { ...item };
    imageDialog.value = true;
}

function openCreateDialog() {
    isEditing.value = false;
    formData.value = {
        id: null,
        product_id: null,
        price: 0,
        bulk_price: storeProfile.value?.use_bulk_pricing ? null : null,
        bulk_min_quantity: storeProfile.value?.use_bulk_pricing ? null : null,
        loyalty_price: storeProfile.value?.has_loyalty_card ? null : null,
        is_active: true,
    };
    dialog.value = true;
}

function openEditDialog(item: StoreProduct) {
    isEditing.value = true;
    formData.value = {
        id: item.id,
        product_id: item.product_id,
        price: item.price,
        bulk_price: storeProfile.value?.use_bulk_pricing ? (item.bulk_price || null) : null,
        bulk_min_quantity: storeProfile.value?.use_bulk_pricing ? (item.bulk_min_quantity || null) : null,
        loyalty_price: storeProfile.value?.has_loyalty_card ? (item.loyalty_price || null) : null,
        is_active: item.is_active,
    };
    dialog.value = true;
}

async function saveProduct() {
    const data = new FormData();
    data.append('product_id', String(formData.value.product_id?.id || formData.value.product_id));
    data.append('price', String(formData.value.price));
    
    // Só envia os campos se a loja permitir
    if (storeProfile.value?.use_bulk_pricing) {
        if (formData.value.bulk_price !== null) data.append('bulk_price', String(formData.value.bulk_price));
        if (formData.value.bulk_min_quantity !== null) data.append('bulk_min_quantity', String(formData.value.bulk_min_quantity));
    }
    
    if (storeProfile.value?.has_loyalty_card && formData.value.loyalty_price !== null) {
        data.append('loyalty_price', String(formData.value.loyalty_price));
    }
    
    data.append('is_active', String(formData.value.is_active));

    try {
        if (isEditing.value && formData.value.id) {
            await storeProductStore.updateStoreProduct(formData.value.id, data);
            snackbarText.value = 'Produto da loja atualizado com sucesso!';
            snackbarColor.value = 'success';
        } else {
            await storeProductStore.createStoreProduct(data);
            snackbarText.value = 'Produto da loja criado com sucesso!';
            snackbarColor.value = 'success';
        }
        dialog.value = false;
    } catch (err) {
        snackbarText.value = storeProductStore.error || 'Erro ao salvar produto da loja';
        snackbarColor.value = 'error';
        console.error('Erro ao salvar produto da loja:', err);
    }
    snackbar.value = true;
}

function confirmDelete(id: number) {
    deleteId.value = id;
    deleteDialog.value = true;
}

async function deleteProduct() {
    if (deleteId.value) {
        try {
            await storeProductStore.deleteStoreProduct(deleteId.value);
            snackbarText.value = 'Produto da loja excluído com sucesso!';
            snackbarColor.value = 'success';
        } catch (err) {
            snackbarText.value = storeProductStore.error || 'Erro ao excluir produto da loja';
            snackbarColor.value = 'error';
        }
        snackbar.value = true;
        deleteDialog.value = false;
        deleteId.value = null;
    }
}
</script>

<style scoped>
.v-list-item__title {
    white-space: normal !important;
}
</style>