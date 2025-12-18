<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Читальные залы</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="readingHalls"
              :loading="loading"
              item-key="id"
            >
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../services/api'

export default {
  name: 'ReadingHalls',
  setup() {
    const readingHalls = ref([])
    const loading = ref(false)
    const headers = [
      { title: 'ID', key: 'id' },
      { title: 'Номер', key: 'number' },
      { title: 'Название', key: 'name' },
      { title: 'Вместимость', key: 'capacity' },
      { title: 'Количество читателей', key: 'readers_count' },
      { title: 'Количество книг', key: 'books_count' }
    ]
    
    const loadReadingHalls = async () => {
      loading.value = true
      try {
        const response = await api.get('/reading-halls/')
        readingHalls.value = response.data.results || response.data
      } catch (error) {
        console.error('Ошибка загрузки читальных залов:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadReadingHalls()
    })
    
    return {
      readingHalls,
      loading,
      headers
    }
  }
}
</script>

