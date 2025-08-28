import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import LeaderboardItem from '../components/LeaderboardItem';

const leaderboardData = [
  { id: '1', name: 'Alice', time: '12:30:00', efficiency: 95 },
  { id: '2', name: 'Bob', time: '11:45:30', efficiency: 88 },
  { id: '3', name: 'Charlie', time: '10:15:45', efficiency: 92 },
  { id: '4', name: 'David', time: '09:30:15', efficiency: 85 },
  { id: '5', name: 'Eve', time: '08:45:00', efficiency: 90 },
];

export default function LeaderboardScreen() {
  return (
    <View style={styles.container}>
      <FlatList
        data={leaderboardData}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <LeaderboardItem user={item} rank={index + 1} />
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
    padding: 10,
  },
});

