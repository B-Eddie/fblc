'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const motivationalMessages = [
  "You've got this! Keep pushing forward!",
  "Every minute of study counts. You're making progress!",
  "Stay focused and achieve your goals. You're doing great!",
  "Believe in yourself. You're capable of amazing things!",
  "Your hard work will pay off. Keep going!",
]

export function MotivationalBot() {
  const [message, setMessage] = useState('')

  const getMotivation = () => {
    const randomIndex = Math.floor(Math.random() * motivationalMessages.length)
    setMessage(motivationalMessages[randomIndex])
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Motivational Bot</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-20 mb-4">
          {message && <p className="text-lg font-medium">{message}</p>}
        </div>
        <Button onClick={getMotivation}>Get Motivation</Button>
      </CardContent>
    </Card>
  )
}

