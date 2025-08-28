'use client'

import { useState } from 'react'
import { StudyTimer } from '../components/study-timer'
import { Leaderboard } from '../components/leaderboard'
import { TaskManager } from '../components/task-manager'
import { MotivationalBot } from '../components/motivational-bot'
import { Chat } from '../components/chat'
import { StudyGraphs } from '../components/study-graphs'
import { SignUp } from '../components/sign-up'
import { SignIn } from '../components/sign-in'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Clock, Trophy, CheckSquare, MessageCircle, Zap, BarChart, UserPlus, LogIn } from 'lucide-react'
import { UserProvider, useUser } from '../contexts/user-context'
import { Button } from "@/components/ui/button"
import { signOut } from './actions/auth'

function Dashboard() {
  const [activeTab, setActiveTab] = useState('timer')
  const { user, setUser } = useUser()

  const handleSignOut = async () => {
    await signOut()
    setUser(null)
  }

  if (!user) {
    return (
      <div className="container px-4 py-8 mx-auto">
        <Tabs defaultValue="signin" className="max-w-md mx-auto">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="signin"><LogIn className="w-4 h-4 mr-2" /> Sign In</TabsTrigger>
            <TabsTrigger value="signup"><UserPlus className="w-4 h-4 mr-2" /> Sign Up</TabsTrigger>
          </TabsList>
          <TabsContent value="signin">
            <SignIn />
          </TabsContent>
          <TabsContent value="signup">
            <SignUp />
          </TabsContent>
        </Tabs>
      </div>
    )
  }

  return (
    <div className="min-h-screen py-8 bg-gray-100">
      <div className="container px-4 mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold">Study Competition Platform</h1>
          <div className="flex items-center gap-4">
            <span>Welcome, {user.email}!</span>
            <Button onClick={handleSignOut}>Sign Out</Button>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-6">
                <TabsTrigger value="timer"><Clock className="w-4 h-4 mr-2" /> Timer</TabsTrigger>
                <TabsTrigger value="leaderboard"><Trophy className="w-4 h-4 mr-2" /> Leaderboard</TabsTrigger>
                <TabsTrigger value="tasks"><CheckSquare className="w-4 h-4 mr-2" /> Tasks</TabsTrigger>
                <TabsTrigger value="chat"><MessageCircle className="w-4 h-4 mr-2" /> Chat</TabsTrigger>
                <TabsTrigger value="motivation"><Zap className="w-4 h-4 mr-2" /> Motivation</TabsTrigger>
                <TabsTrigger value="graphs"><BarChart className="w-4 h-4 mr-2" /> Graphs</TabsTrigger>
              </TabsList>
              <TabsContent value="timer">
                <StudyTimer />
              </TabsContent>
              <TabsContent value="leaderboard">
                <Leaderboard />
              </TabsContent>
              <TabsContent value="tasks">
                <TaskManager />
              </TabsContent>
              <TabsContent value="chat">
                <Chat />
              </TabsContent>
              <TabsContent value="motivation">
                <MotivationalBot />
              </TabsContent>
              <TabsContent value="graphs" className="p-4">
                <StudyGraphs />
              </TabsContent>
            </Tabs>
          </div>
          <div className="space-y-8 lg:col-span-1">
            <div className="sticky top-8">
              <Leaderboard />
              <div className="mt-8">
                <StudyGraphs />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Home() {
  return (
    <UserProvider>
      <Dashboard />
    </UserProvider>
  )
}

