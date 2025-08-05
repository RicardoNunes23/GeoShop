<template>
  <div style="height:400px; width:100%; position:relative;">
    <LMap
      ref="map"
      :zoom="zoom"
      :center="initialCenter"
      :use-global-leaflet="false"
      @ready="onMapReady"
    >
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&amp;copy; <a href=&quot;https://www.openstreetmap.org/&quot;>OpenStreetMap</a> contributors"
        layer-type="base"
        name="OpenStreetMap"
      />
      
      <LMarker
        v-for="(store, index) in stores"
        :key="index"
        :lat-lng="store.latLng"
        @click="onMarkerClick(store)"
      >
        <LPopup>
          <div>
            <strong>{{ store.name }}</strong>
            <p v-if="store.total_price">Preço total: {{ store.total_price }}</p>
            <p v-if="store.items_count">Itens disponíveis: {{ store.items_count }}</p>
            <p v-if="store.distance">Distância: {{ store.distance }} km</p>
          </div>
        </LPopup>
        
        <LIcon
          :icon-url="store.iconUrl"
          :icon-size="[32, 32]"
          :icon-anchor="[16, 32]"
        />
      </LMarker>
    </LMap>
    
    <div class="map-legend">
      <div><span class="legend-icon green"></span> Preço baixo</div>
      <div><span class="legend-icon gold"></span> Preço médio</div>
      <div><span class="legend-icon red"></span> Preço alto</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { LMap, LTileLayer, LMarker, LPopup, LIcon } from '@vue-leaflet/vue-leaflet';
import 'leaflet/dist/leaflet.css';
import type { LatLngExpression, Map } from 'leaflet';

interface StoreMarker {
  id: number;
  name: string;
  latLng: LatLngExpression;
  total_price?: string;
  items_count?: number;
  distance?: number;
  iconUrl: string;
}

const props = defineProps({
  stores: {
    type: Array as () => StoreMarker[],
    required: true
  },
  userLocation: {
    type: Array as () => [number, number],
    default: null
  }
});

const emit = defineEmits(['marker-click']);

const zoom = ref(13);
const initialCenter = ref<LatLngExpression>([-23.5505, -46.6333]); // Centro padrão (São Paulo)
const map = ref<{leafletObject: Map} | null>(null);
let mapInstance: Map | null = null;

const onMapReady = () => {
  if (map.value) {
    mapInstance = map.value.leafletObject;
    if (props.stores.length > 0) {
      zoomToStores();
    } else if (props.userLocation) {
      mapInstance.setView(props.userLocation, 15);
    }
  }
};

const zoomToStores = () => {
  if (!mapInstance || props.stores.length === 0) return;
  
  if (props.stores.length === 1) {
    mapInstance.setView(props.stores[0].latLng, 15);
  } else {
    const bounds = props.stores.map(store => store.latLng);
    mapInstance.fitBounds(bounds, { padding: [50, 50] });
  }
};

const onMarkerClick = (store: StoreMarker) => {
  emit('marker-click', store);
  if (mapInstance) {
    mapInstance.setView(store.latLng, 15);
  }
};

watch(() => props.stores, () => {
  if (props.stores.length > 0) {
    zoomToStores();
  }
}, { deep: true });

watch(() => props.userLocation, (newLoc) => {
  if (newLoc && mapInstance) {
    mapInstance.setView(newLoc, 15);
  }
});

onUnmounted(() => {
  if (mapInstance) {
    mapInstance.remove();
    mapInstance = null;
  }
});
</script>

<style scoped>
.leaflet-container {
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  height: 100%;
  width: 100%;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
  z-index: 1000;
  font-size: 12px;
}

.legend-icon {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
}

.legend-icon.green {
  background-color: #2ecc71;
}

.legend-icon.gold {
  background-color: #f1c40f;
}

.legend-icon.red {
  background-color: #e74c3c;
}
</style>