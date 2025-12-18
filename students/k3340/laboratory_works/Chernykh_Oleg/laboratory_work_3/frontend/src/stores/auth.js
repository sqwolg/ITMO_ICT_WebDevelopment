import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/token/login/', {
        username,
        password
      })
      token.value = response.data.auth_token
      localStorage.setItem('token', token.value)
      
      const userResponse = await api.get('/auth/users/me/')
      user.value = userResponse.data
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.non_field_errors?.[0] || 'Ошибка входа' 
      }
    }
  }

  const register = async (username, password, passwordConfirm) => {
    try {
      const response = await api.post('/auth/users/', {
        username,
        password,
        re_password: passwordConfirm
      })
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Ошибка регистрации' 
      }
    }
  }

  const updateProfile = async (data) => {
    try {
      const response = await api.patch('/auth/users/me/', data)
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(user.value))
      return { success: true, data: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Ошибка обновления профиля' 
      }
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    try {
      await api.post('/auth/users/set_password/', {
        current_password: currentPassword,
        new_password: newPassword,
        re_new_password: newPassword
      })
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Ошибка смены пароля' 
      }
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    updateProfile,
    changePassword,
    logout
  }
})

