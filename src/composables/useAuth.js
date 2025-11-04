import { ref, onMounted } from 'vue'
import { supabase } from '../supabase'

const user = ref(null)
const loading = ref(true)
const isAdmin = ref(false)

export function useAuth() {
  // Check if user is logged in
  const checkUser = async (minDelay = 2000) => {
    loading.value = true
    const startTime = Date.now()

    const { data: { session } } = await supabase.auth.getSession()
    user.value = session?.user || null

    // Check if user is admin (you can set this in Supabase user metadata)
    if (user.value) {
      isAdmin.value = user.value.user_metadata?.role === 'admin' ||
                      user.value.email === 'admin@fueldock.ee' || // Fallback admin email
                      user.value.email === 'uve.mae@gmail.com' // Admin email
    }

    // Ensure loading screen shows for at least minDelay milliseconds
    const elapsedTime = Date.now() - startTime
    const remainingTime = Math.max(0, minDelay - elapsedTime)

    await new Promise(resolve => setTimeout(resolve, remainingTime))
    loading.value = false
  }

  // Sign up with email
  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: window.location.origin
      }
    })

    if (error) throw error
    return data
  }

  // Sign in with email
  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) throw error
    user.value = data.user

    // Check admin status after login
    if (user.value) {
      isAdmin.value = user.value.user_metadata?.role === 'admin' ||
                      user.value.email === 'admin@fueldock.ee' ||
                      user.value.email === 'uve.mae@gmail.com'
    }

    return data
  }

  // Sign out
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    user.value = null
    isAdmin.value = false
  }

  // Reset password
  const resetPassword = async (email) => {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })
    if (error) throw error
  }

  // Listen to auth changes
  const initAuthListener = () => {
    supabase.auth.onAuthStateChange((event, session) => {
      user.value = session?.user || null

      if (user.value) {
        isAdmin.value = user.value.user_metadata?.role === 'admin' ||
                        user.value.email === 'admin@fueldock.ee' ||
                        user.value.email === 'uve.mae@gmail.com'
      } else {
        isAdmin.value = false
      }

      loading.value = false
    })
  }

  return {
    user,
    loading,
    isAdmin,
    checkUser,
    signUp,
    signIn,
    signOut,
    resetPassword,
    initAuthListener
  }
}
