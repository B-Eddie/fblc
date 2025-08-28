'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Send } from 'lucide-react'

type Message = {
  id: number
  sender: string
  content: string
  timestamp: Date
}

const initialMessages: Message[] = [
  { id: 1, sender: 'Alice', content: 'Hey, how\'s your study session going?', timestamp: new Date('2023-05-10T10:00:00') },
  { id: 2, sender: 'You', content: 'Pretty good! I\'m working on math right now.', timestamp: new Date('2023-05-10T10:05:00') },
  { id: 3, sender: 'Alice', content: 'Nice! I\'m tackling some history. Want to compete?', timestamp: new Date('2023-05-10T10:07:00') },
]

export function Chat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [newMessage, setNewMessage] = useState('')

  const sendMessage = () => {
    if (newMessage.trim() !== '') {
      const message: Message = {
        id: messages.length + 1,
        sender: 'You',
        content: newMessage,
        timestamp: new Date(),
      }
      setMessages([...messages, message])
      setNewMessage('')
    }
  }

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle>Chat with Friends</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col flex-grow">
        <ScrollArea className="flex-grow mb-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex mb-4 ${message.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex ${message.sender === 'You' ? 'flex-row-reverse' : 'flex-row'} items-start`}>
                <Avatar className="w-8 h-8">
                  <AvatarImage src={`https://api.dicebear.com/6.x/initials/svg?seed=${message.sender}`} />
                  <AvatarFallback>{message.sender[0]}</AvatarFallback>
                </Avatar>
                <div className={`mx-2 ${message.sender === 'You' ? 'text-right' : 'text-left'}`}>
                  <p className="text-sm font-semibold">{message.sender}</p>
                  <div className={`mt-1 p-2 rounded-lg ${message.sender === 'You' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
                    {message.content}
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </ScrollArea>
        <div className="flex items-center">
          <Input
            type="text"
            placeholder="Type a message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            className="flex-grow"
          />
          <Button onClick={sendMessage} className="ml-2">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

