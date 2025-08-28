import auth from '@react-native-firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';

export async function signUp(email: string, password: string) {
  try {
    const userCredential = await auth().createUserWithEmailAndPassword(email, password);
    const user = userCredential.user;
    await AsyncStorage.setItem('user', JSON.stringify({ uid: user.uid, email: user.email }));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export async function signIn(email: string, password: string) {
  try {
    const userCredential = await auth().signInWithEmailAndPassword(email, password);
    const user = userCredential.user;
    await AsyncStorage.setItem('user', JSON.stringify({ uid: user.uid, email: user.email }));
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export async function signOut() {
  try {
    await auth().signOut();
    await AsyncStorage.removeItem('user');
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export async function getUser() {
  try {
    const userJson = await AsyncStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
  } catch (error) {
    console.error('Error getting user from AsyncStorage:', error);
    return null;
  }
}

