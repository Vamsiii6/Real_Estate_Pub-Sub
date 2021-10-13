import firebase from 'firebase'

const firebaseConfig = {
  apiKey: 'AIzaSyCsOVvTdOXLrdNLI6rYR09mWA-c714SVfU',
  authDomain: 'ds-project1-186c7.firebaseapp.com',
  projectId: 'ds-project1-186c7',
  storageBucket: 'ds-project1-186c7.appspot.com',
  messagingSenderId: '311493106346',
  appId: '1:311493106346:web:a67cba2733af95b4658ed3',
  measurementId: 'G-61HYG15Z52',
}

const app = firebase.initializeApp(firebaseConfig)
const auth = app.auth()
export { auth }
