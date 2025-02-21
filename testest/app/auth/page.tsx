"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from "firebase/auth"
import { auth } from "@/lib/firebase"
import { useAuth } from "@/hooks/useAuth"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function Auth() {
  useAuth(false) // Redirect to dashboard if user is already logged in
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLogin, setIsLogin] = useState(true)
  const [error, setError] = useState("")
  const router = useRouter()

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password)
      } else {
        await createUserWithEmailAndPassword(auth, email, password)
      }
      router.push("/dashboard")
    } catch (error: any) {
      console.error("Authentication error:", error)
      setError(error.message || "An error occurred during authentication")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-orange-50">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-md w-full mx-auto p-8 bg-white rounded-lg shadow-xl"
      >
        <h2 className="text-3xl font-bold text-orange-600 mb-6 text-center">{isLogin ? "Login" : "Sign Up"}</h2>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        <form onSubmit={handleAuth} className="space-y-4">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full"
            required
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full"
            required
          />
          <Button type="submit" className="w-full bg-orange-600 hover:bg-orange-700 text-white">
            {isLogin ? "Login" : "Sign Up"}
          </Button>
        </form>
        <motion.p
          className="mt-4 text-center text-orange-600 cursor-pointer"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsLogin(!isLogin)}
        >
          {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
        </motion.p>
      </motion.div>
    </div>
  )
}

