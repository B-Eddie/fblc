import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView } from 'react-native';
import { useUser } from '../contexts/UserContext';
import StudyGraphs from '../components/StudyGraphs';
import { Button } from 'react-native-elements';
import auth from '@react-native-firebase/auth';

export default function ProfileScreen() {
  const { user } = useUser();

  const handleSignOut = async () => {
    try {
      await auth().signOut();
    } catch (error) {
      console.error('Error signing out: ', error);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Image
          style={styles.avatar}
          source={{ uri: `https://i.pravatar.cc/150?u=${user?.email}` }}
        />
        <Text style={styles.username}>{user?.email}</Text>
      </View>
      <View style={styles.stats}>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>120h</Text>
          <Text style={styles.statLabel}>Total Study Time</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>92%</Text>
          <Text style={styles.statLabel}>Efficiency</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>15</Text>
          <Text style={styles.statLabel}>Streak Days</Text>
        </View>
      </View>
      <StudyGraphs />
      <Button
        title="Sign Out"
        onPress={handleSignOut}
        buttonStyle={styles.signOutButton}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
  },
  header: {
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 10,
  },
  username: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
  },
  signOutButton: {
    backgroundColor: '#405DE6',
    marginHorizontal: 20,
    marginVertical: 20,
  },
});

