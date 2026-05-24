// Persistencia liviana del user_id en localStorage
const USER_KEY = 'tracker:user_id'

export const storage = {
  getUserId: () => localStorage.getItem(USER_KEY),
  setUserId: (id: string) => localStorage.setItem(USER_KEY, id),
  clear: () => localStorage.removeItem(USER_KEY),
}
