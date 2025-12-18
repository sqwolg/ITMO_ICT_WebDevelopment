<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Читатели</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="readers"
              :loading="loading"
              item-key="id"
            >
              <template v-slot:item.reading_hall_detail="{ item }">
                {{ item.reading_hall_detail ? item.reading_hall_detail.name : '-' }}
              </template>
              <template v-slot:item.education="{ item }">
                {{ getEducationLabel(item.education) }}
              </template>
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
  name: 'Readers',
  setup() {
    const readers = ref([])
    const loading = ref(false)
    const headers = [
      { title: 'ID', key: 'id' },
      { title: 'Номер билета', key: 'ticket_number' },
      { title: 'ФИО', key: 'full_name' },
      { title: 'Паспорт', key: 'passport_number' },
      { title: 'Дата рождения', key: 'birth_date' },
      { title: 'Образование', key: 'education' },
      { title: 'Читальный зал', key: 'reading_hall_detail' }
    ]
    
    const getEducationLabel = (education) => {
      const labels = {
        'primary': 'Начальное',
        'secondary': 'Среднее',
        'higher': 'Высшее',
        'degree': 'Ученая степень'
      }
      return labels[education] || education
    }
    
    const loadReaders = async () => {
      loading.value = true
      try {
        const response = await api.get('/readers/')
        readers.value = response.data.results || response.data
      } catch (error) {
        console.error('Ошибка загрузки читателей:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadReaders()
    })
    
    return {
      readers,
      loading,
      headers,
      getEducationLabel
    }
  }
}
</script>

