// Persistencia liviana de sesión en localStorage (F1)
const USER_KEY = 'tracker:user_id'
const TOKEN_KEY = 'tracker:access_token'

export const storage = {
  getUserId: () => localStorage.getItem(USER_KEY),
  setUserId: (id: string) => localStorage.setItem(USER_KEY, id),

  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => localStorage.setItem(TOKEN_KEY, token),

  // Guarda user_id + token en una sola operación (tras register/login)
  setSession: (userId: string, token: string) => {
    localStorage.setItem(USER_KEY, userId)
    localStorage.setItem(TOKEN_KEY, token)
  },

  clear: () => {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TOKEN_KEY)
  },
}
