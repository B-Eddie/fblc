import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';

interface LeaderboardItemProps {
  user: {
    name: string;
    time: string;
    efficiency: number;
  };
  rank: number;
}

export default function LeaderboardItem({ user, rank }: LeaderboardItemProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.rank}>{rank}</Text>
      <Image
        style={styles.avatar}
        source={{ uri: `https://i.pravatar.cc/150?u=${user.name}` }}
      />
      <View style={styles.info}>
        <Text style={styles.name}>{user.name}</Text>
        <Text style={styles.stats}>
          Time: {user.time} | Efficiency: {user.efficiency}%
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
  },
  rank: {
    fontSize: 18,
    fontWeight: 'bold',
    marginRight: 15,
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 15,
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  stats: {
    fontSize: 14,
    color: '#666',
  },
});

