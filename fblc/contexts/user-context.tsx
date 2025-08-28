'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { getUser } from '@/app/actions/auth'

type User = {
  username: string
} | null

type UserContextType = {
  user: User
  setUser: React.Dispatch<React.SetStateAction<User>>
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User>(null)

  useEffect(() => {
    getUser().then(setUser)
  }, [])

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

