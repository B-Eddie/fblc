import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import StudyPost from '../components/StudyPost';

const dummyPosts = [
  { id: '1', username: 'alice', studyTime: '2h 30m', subject: 'Math', imageUrl: 'https://picsum.photos/400/400' },
  { id: '2', username: 'bob', studyTime: '1h 45m', subject: 'History', imageUrl: 'https://picsum.photos/400/401' },
  { id: '3', username: 'charlie', studyTime: '3h 15m', subject: 'Science', imageUrl: 'https://picsum.photos/400/402' },
];

export default function FeedScreen() {
  return (
    <View style={styles.container}>
      <FlatList
        data={dummyPosts}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <StudyPost post={item} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fafafa',
  },
});

