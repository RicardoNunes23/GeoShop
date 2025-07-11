<template>
  <div ref="mapContainer" class="map-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Props para configurar o mapa e marcadores
const props = defineProps({
  center: {
    type: Array,
    default: () => [-23.5505, -46.6333], // Centro padrão (São Paulo)
    validator: (value) => value.length === 2 && value.every(Number.isFinite)
  },
  zoom: {
    type: Number,
    default: 13
  },
  markers: {
    type: Array,
    default: () => [],
    validator: (value) => value.every(marker => 
      Array.isArray(marker.coords) && 
      marker.coords.length === 2 && 
      marker.coords.every(Number.isFinite)
    )
  }
})

// Referência ao container do mapa
const mapContainer = ref(null)
let map = null

// Função para inicializar o mapa
const initMap = () => {
  if (!mapContainer.value) return

  // Criar o mapa
  map = L.map(mapContainer.value).setView(props.center, props.zoom)

  // Adicionar camada de tiles do OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map)

  // Adicionar marcadores iniciais
  updateMarkers()
}

// Função para atualizar marcadores
const updateMarkers = () => {
  if (!map) return

  // Remover marcadores existentes (exceto a camada de tiles)
  map.eachLayer(layer => {
    if (layer instanceof L.Marker) {
      map.removeLayer(layer)
    }
  })

  // Adicionar novos marcadores
  props.markers.forEach(marker => {
    const { coords, popup } = marker
    const markerInstance = L.marker(coords).addTo(map)
    
    if (popup) {
      markerInstance.bindPopup(popup)
    }
  })
}

// Inicializar o mapa quando o componente for montado
onMounted(() => {
  initMap()
})

// Limpar o mapa quando o componente for desmontado
onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

// Observar mudanças nas props de marcadores e centro
watch(() => [props.center, props.markers], () => {
  if (map) {
    map.setView(props.center, props.zoom)
    updateMarkers()
  }
}, { deep: true })
</script>

<style scoped>
.map-container {
  height: 400px;
  width: 100%;
}

/* Corrigir ícone do marcador padrão do Leaflet */
:deep(.leaflet-marker-icon) {
  background-image: url('https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png');
}
</style>