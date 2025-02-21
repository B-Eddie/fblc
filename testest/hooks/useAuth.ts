"use client"

import { useEffect } from "react"
import { useRouter } from "next/router"
import { useAuthState } from "react-firebase-hooks/auth"
import { auth } from "@/lib/firebase"

export function useAuth(requireAuth = true) {
  const [user, loading] = useAuthState(auth)
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (requireAuth && !user) {
        router.push("/")
      } else if (!requireAuth && user) {
        router.push("/dashboard")
      }
    }
  }, [user, loading, requireAuth, router])

  return { user, loading }
}

