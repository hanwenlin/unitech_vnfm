import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const username = ref<string | null>(localStorage.getItem('username'))

  async function login(usernameVal: string, passwordVal: string) {
    const form = new URLSearchParams()
    form.append('username', usernameVal)
    form.append('password', passwordVal)
    const res = await api.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    token.value = res.data.access_token
    username.value = usernameVal
    localStorage.setItem('token', token.value)
    localStorage.setItem('username', usernameVal)
  }

  function logout() {
    token.value = null
    username.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }

  return { token, username, login, logout }
})
