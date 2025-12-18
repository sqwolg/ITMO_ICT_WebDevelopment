<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Профиль</v-card-title>
          <v-card-text>
            <v-tabs v-model="tab">
              <v-tab value="profile">Профиль</v-tab>
              <v-tab value="password">Смена пароля</v-tab>
            </v-tabs>
            
            <v-window v-model="tab">
              <v-window-item value="profile">
                <v-form @submit.prevent="handleUpdateProfile" class="mt-4">
                  <v-text-field
                    v-model="profileData.username"
                    label="Имя пользователя"
                    variant="outlined"
                  ></v-text-field>
                  <v-text-field
                    v-model="profileData.email"
                    label="Email"
                    variant="outlined"
                  ></v-text-field>
                  <v-text-field
                    v-model="profileData.first_name"
                    label="Имя"
                    variant="outlined"
                  ></v-text-field>
                  <v-text-field
                    v-model="profileData.last_name"
                    label="Фамилия"
                    variant="outlined"
                  ></v-text-field>
                  <v-alert v-if="profileError" type="error" class="mb-4">{{ profileError }}</v-alert>
                  <v-alert v-if="profileSuccess" type="success" class="mb-4">Профиль обновлен</v-alert>
                  <v-btn type="submit" color="primary">Сохранить</v-btn>
                </v-form>
              </v-window-item>
              
              <v-window-item value="password">
                <v-form @submit.prevent="handleChangePassword" class="mt-4">
                  <v-text-field
                    v-model="passwordData.currentPassword"
                    label="Текущий пароль"
                    type="password"
                    variant="outlined"
                  ></v-text-field>
                  <v-text-field
                    v-model="passwordData.newPassword"
                    label="Новый пароль"
                    type="password"
                    variant="outlined"
                  ></v-text-field>
                  <v-text-field
                    v-model="passwordData.newPasswordConfirm"
                    label="Подтверждение нового пароля"
                    type="password"
                    variant="outlined"
                  ></v-text-field>
                  <v-alert v-if="passwordError" type="error" class="mb-4">{{ passwordError }}</v-alert>
                  <v-alert v-if="passwordSuccess" type="success" class="mb-4">Пароль изменен</v-alert>
                  <v-btn type="submit" color="primary">Изменить пароль</v-btn>
                </v-form>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    
    const tab = ref('profile')
    const profileError = ref('')
    const profileSuccess = ref(false)
    const passwordError = ref('')
    const passwordSuccess = ref(false)
    
    const profileData = ref({
      username: '',
      email: '',
      first_name: '',
      last_name: ''
    })
    
    const passwordData = ref({
      currentPassword: '',
      newPassword: '',
      newPasswordConfirm: ''
    })
    
    onMounted(() => {
      if (authStore.user) {
        profileData.value = {
          username: authStore.user.username || '',
          email: authStore.user.email || '',
          first_name: authStore.user.first_name || '',
          last_name: authStore.user.last_name || ''
        }
      }
    })
    
    const handleUpdateProfile = async () => {
      profileError.value = ''
      profileSuccess.value = false
      const result = await authStore.updateProfile(profileData.value)
      if (result.success) {
        profileSuccess.value = true
      } else {
        profileError.value = typeof result.error === 'string' ? result.error : JSON.stringify(result.error)
      }
    }
    
    const handleChangePassword = async () => {
      passwordError.value = ''
      passwordSuccess.value = false
      if (passwordData.value.newPassword !== passwordData.value.newPasswordConfirm) {
        passwordError.value = 'Пароли не совпадают'
        return
      }
      const result = await authStore.changePassword(
        passwordData.value.currentPassword,
        passwordData.value.newPassword
      )
      if (result.success) {
        passwordSuccess.value = true
        passwordData.value = {
          currentPassword: '',
          newPassword: '',
          newPasswordConfirm: ''
        }
      } else {
        passwordError.value = typeof result.error === 'string' ? result.error : JSON.stringify(result.error)
      }
    }
    
    return {
      tab,
      profileData,
      passwordData,
      profileError,
      profileSuccess,
      passwordError,
      passwordSuccess,
      handleUpdateProfile,
      handleChangePassword
    }
  }
}
</script>

