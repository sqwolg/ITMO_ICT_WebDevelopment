<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <v-card-title class="text-h5">Регистрация</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
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
              <v-text-field
                v-model="passwordConfirm"
                label="Подтверждение пароля"
                type="password"
                required
                variant="outlined"
              ></v-text-field>
              <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>
              <v-btn type="submit" color="primary" block>Зарегистрироваться</v-btn>
            </v-form>
            <v-divider class="my-4"></v-divider>
            <v-btn to="/login" variant="text" block>Вход</v-btn>
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
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const username = ref('')
    const password = ref('')
    const passwordConfirm = ref('')
    const error = ref('')
    
    const handleRegister = async () => {
      error.value = ''
      if (password.value !== passwordConfirm.value) {
        error.value = 'Пароли не совпадают'
        return
      }
      const result = await authStore.register(username.value, password.value, passwordConfirm.value)
      if (result.success) {
        router.push('/login')
      } else {
        error.value = typeof result.error === 'string' ? result.error : JSON.stringify(result.error)
      }
    }
    
    return {
      username,
      password,
      passwordConfirm,
      error,
      handleRegister
    }
  }
}
</script>

