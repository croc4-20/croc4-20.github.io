if (!firebase.apps.length) {
    console.log("Initializing Firebase...");
    firebase.initializeApp({
        apiKey: "AIzaSyAPqPvrJMC1Kd7M3aWIJKRZPBnQKwAIc_g",
        authDomain: "pixel-a188a.firebaseapp.com",
        projectId: "pixel-a188a",
        storageBucket: "pixel-a188a.appspot.com",
        messagingSenderId: "1051565452085",
        appId: "1:1051565452085:web:38846df63666fd719f3a7c"
    });
} else {
    console.log("Firebase already initialized.");
}
