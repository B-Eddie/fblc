import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const leaderboardData = [
  { name: 'Alice', time: '12:30:00', efficiency: 95 },
  { name: 'Bob', time: '11:45:30', efficiency: 88 },
  { name: 'Charlie', time: '10:15:45', efficiency: 92 },
  { name: 'David', time: '09:30:15', efficiency: 85 },
  { name: 'Eve', time: '08:45:00', efficiency: 90 },
]

export function Leaderboard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Leaderboard</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {leaderboardData.map((user, index) => (
            <div key={index} className="flex items-center space-x-4">
              <Avatar>
                <AvatarImage src={`https://api.dicebear.com/6.x/initials/svg?seed=${user.name}`} />
                <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-gray-500">Time: {user.time}</p>
              </div>
              <div className="text-sm font-medium">Efficiency: {user.efficiency}%</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

