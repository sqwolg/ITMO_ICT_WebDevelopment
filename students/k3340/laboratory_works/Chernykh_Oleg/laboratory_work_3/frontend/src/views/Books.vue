<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Книги</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="books"
              :loading="loading"
              item-key="id"
            >
              <template v-slot:item.authors_detail="{ item }">
                <span v-for="(author, index) in item.authors_detail" :key="author.id">
                  {{ author.name }}<span v-if="index < item.authors_detail.length - 1">, </span>
                </span>
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
  name: 'Books',
  setup() {
    const books = ref([])
    const loading = ref(false)
    const headers = [
      { title: 'ID', key: 'id' },
      { title: 'Название', key: 'title' },
      { title: 'Авторы', key: 'authors_detail' },
      { title: 'Издательство', key: 'publisher' },
      { title: 'Год издания', key: 'publication_year' },
      { title: 'Раздел', key: 'section' },
      { title: 'Шифр', key: 'code' }
    ]
    
    const loadBooks = async () => {
      loading.value = true
      try {
        const response = await api.get('/books/')
        books.value = response.data.results || response.data
      } catch (error) {
        console.error('Ошибка загрузки книг:', error)
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      loadBooks()
    })
    
    return {
      books,
      loading,
      headers
    }
  }
}
</script>

