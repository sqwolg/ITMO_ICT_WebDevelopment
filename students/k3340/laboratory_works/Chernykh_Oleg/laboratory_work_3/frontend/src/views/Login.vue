<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-h5">Вход</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                required
                variant="outlined"
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Пароль"
                type="password"
                required
                variant="outlined"
              ></v-text-field>
              <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
              <v-btn type="submit" color="primary" block>Войти</v-btn>
            </v-form>
            <v-divider class="my-4"></v-divider>
            <v-btn to="/register" variant="text" block>Регистрация</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const error = ref('')
    
    const handleLogin = async () => {
      error.value = ''
      const result = await authStore.login(username.value, password.value)
      if (result.success) {
        router.push('/books')
      } else {
        error.value = result.error
      }
    }
    
    return {
      username,
      password,
      error,
      handleLogin
    }
  }
}
</script>

