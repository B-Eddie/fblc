import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';

const leaderboardData = [
  { name: 'Alice', time: '12:30:00', efficiency: 95 },
  { name: 'Bob', time: '11:45:30', efficiency: 88 },
  { name: 'Charlie', time: '10:15:45', efficiency: 92 },
  { name: 'David', time: '09:30:15', efficiency: 85 },
  { name: 'Eve', time: '08:45:00', efficiency: 90 },
];

export default function Leaderboard() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Leaderboard</Text>
      <FlatList
        data={leaderboardData}
        keyExtractor={(item) => item.name}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <View style={styles.userInfo}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.time}>Time: {item.time}</Text>
            </View>
            <Text style={styles.efficiency}>Efficiency: {item.efficiency}%</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  userInfo: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  time: {
    fontSize: 14,
    color: '#666',
  },
  efficiency: {
    fontSize: 14,
    fontWeight: 'bold',
  },
});

