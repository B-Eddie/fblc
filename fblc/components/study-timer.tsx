'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useUser } from '../contexts/user-context'
import { database } from '@/lib/firebase'
import { ref, onValue, set } from 'firebase/database'

export function StudyTimer() {
  const [time, setTime] = useState(0)
  const [isActive, setIsActive] = useState(false)
  const { user } = useUser()

  useEffect(() => {
    if (!user) return

    const timerRef = ref(database, `users/${user.uid}/timer`)
    const unsubscribe = onValue(timerRef, (snapshot) => {
      const data = snapshot.val()
      if (data) {
        setTime(data.time)
        setIsActive(data.isActive)
      }
    })

    return () => unsubscribe()
  }, [user])

  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isActive) {
      interval = setInterval(() => {
        setTime((prevTime) => {
          const newTime = prevTime + 1
          if (user) {
            set(ref(database, `users/${user.uid}/timer`), {
              time: newTime,
              isActive: true
            })
          }
          return newTime
        })
      }, 1000)
    }

    return () => clearInterval(interval)
  }, [isActive, user])

  const toggleTimer = () => {
    const newIsActive = !isActive
    setIsActive(newIsActive)
    if (user) {
      set(ref(database, `users/${user.uid}/timer`), {
        time,
        isActive: newIsActive
      })
    }
  }

  const resetTimer = () => {
    setTime(0)
    setIsActive(false)
    if (user) {
      set(ref(database, `users/${user.uid}/timer`), {
        time: 0,
        isActive: false
      })
    }
  }

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const remainingSeconds = seconds % 60
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Study Timer for {user?.email}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 text-4xl font-bold">{formatTime(time)}</div>
        <div className="space-x-2">
          <Button onClick={toggleTimer}>{isActive ? 'Pause' : 'Start'}</Button>
          <Button onClick={resetTimer} variant="outline">
            Reset
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

