<template>
  <v-app>
    <v-app-bar v-if="isAuthenticated" color="primary" dark>
      <v-app-bar-title>Библиотека</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn to="/books" variant="text">Книги</v-btn>
      <v-btn to="/readers" variant="text">Читатели</v-btn>
      <v-btn to="/reading-halls" variant="text">Читальные залы</v-btn>
      <v-btn to="/profile" variant="text">Профиль</v-btn>
      <v-btn @click="logout" variant="text">Выход</v-btn>
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    const logout = () => {
      authStore.logout()
      router.push('/login')
    }
    
    return {
      isAuthenticated,
      logout
    }
  }
}
</script>

