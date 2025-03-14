if (!firebase.apps.length) {
    console.log("Initializing Firebase...");
    firebase.initializeApp({
        apiKey: "AIzaSyAPqPvrJMC1Kd7M3aWIJKRZPBnQKwAIc_g",
        authDomain: "pixel-a188a.firebaseapp.com",
        projectId: "pixel-a188a",
        storageBucket: "pixel-a188a.firebasestorage.app",
        messagingSenderId: "1051565452085",
        appId: "1:1051565452085:web:38846df63666fd719f3a7c"
    });
} else {
    console.log("Firebase already initialized.");
}




// Ensure that our merged library container exists.
// Try to use LibraryManager if available; if not, create it.
if (typeof LibraryManager === "undefined") {
    console.warn("LibraryManager is not defined; creating a fallback object.");
    LibraryManager = { library: {} };
} else if (!LibraryManager.library) {
    LibraryManager.library = {};
}

// Expose GetLeaderboardData globally.
// We check both LibraryManager.library and Module for the function.
if (typeof window !== 'undefined') {
    window.GetLeaderboardData = function() {
        var getLBFunc = null;
        if (LibraryManager && LibraryManager.library && typeof LibraryManager.library.GetLeaderboardData === "function") {
            getLBFunc = LibraryManager.library.GetLeaderboardData;
        } else if (typeof Module !== "undefined" && typeof Module.GetLeaderboardData === "function") {
            getLBFunc = Module.GetLeaderboardData;
        }
        if (getLBFunc) {
            // Call the merged function. Since our merged function now doesn't use a callback pointer,
            // we pass 0 (or modify your merged code accordingly).
            getLBFunc(0);
        } else {
            console.error("GetLeaderboardData function is not available in LibraryManager or Module.");
        }
    };
}
function safeSendMessage(objectName, methodName, message) {
    if (typeof SendMessage === "function") {
        SendMessage(objectName, methodName, message);
    } else {
        console.warn(`🔄 Waiting for Unity's SendMessage: ${methodName}`);
        setTimeout(() => safeSendMessage(objectName, methodName, message), 100);
    }
}
if (typeof window !== 'undefined') {
  window.GetUserRobots = function(userId) {
    if (!firebase.firestore) {
      console.error("Firestore is not available!");
      return;
    }
    var db = firebase.firestore();
    db.collection("users").doc(userId).collection("robots").get()
      .then((querySnapshot) => {
        let robots = [];
        querySnapshot.forEach((doc) => {
          let data = doc.data();
          data._robotId = doc.id; // store the doc ID for reference
          robots.push(data);
        });
        let robotsJson = JSON.stringify(robots);
        // Send the array of robots back to Unity

        safeSendMessage("FireBaseManager", "OnUserRobotsReceived", robotsJson);

        // SendMessage("FireBaseManager", "OnUserRobotsReceived", robotsJson);
      })
      .catch((error) => {
        console.error("❌ Error fetching user robots: ", error);
        // Optionally send an error message back to Unity
        SendMessage("FireBaseManager", "OnUserRobotsReceived", "error");
      });
  };
}


if (typeof window !== 'undefined') {
  window.SaveRobotData = function(userId, robotId, robotJson) {
    if (!firebase.firestore) {
        console.error("Firestore is not available!");
        return;
    }

    var db = firebase.firestore();
    var robotData = JSON.parse(robotJson); // Convert string to JSON object

    db.collection("customRobots").doc(userId).collection("robots").doc(robotId).set(robotData)
        .then(() => {
            console.log(`✅ Robot ${robotId} saved successfully for user ${userId}.`);
            SendMessage("FireBaseManager", "OnRobotDataSaved", "success");
        })
        .catch((error) => {
            console.error("❌ Error saving robot: ", error);
            SendMessage("FireBaseManager", "OnRobotDataSaved", "error");
        });
};
}

// (function() {
//     // Initialize Firebase if not already initialized.
//     if (!firebase.apps.length) {
//         console.log("Initializing Firebase...");
//         firebase.initializeApp({
//             apiKey: "AIzaSyAPqPvrJMC1Kd7M3aWIJKRZPBnQKwAIc_g",
//             authDomain: "pixel-a188a.firebaseapp.com",
//             projectId: "pixel-a188a",
//             storageBucket: "pixel-a188a.appspot.com",
//             messagingSenderId: "1051565452085",
//             appId: "1:1051565452085:web:38846df63666fd719f3a7c"
//         });
//     } else {
//         console.log("Firebase already initialized.");
//     }

//     // Function to call when Unity's SendMessage is available.
//     function callSendMessage(leaderboardJson) {
//         console.log("Leaderboard JSON: " + leaderboardJson);
//         SendMessage("PhotonManagerScript", "OnLeaderboardDataReceived", leaderboardJson);
//     }

//     // Define a global function for fetching leaderboard data.
//     window.GetLeaderboardData = function() {
//         console.log("GetLeaderboardData called from global scope.");
//         if (typeof firebase === 'undefined' || !firebase.firestore) {
//             console.error("Firebase Firestore is not available!");
//             return;
//         }
//         var db = firebase.firestore();
//         db.collection('RobotUsers')
//           .orderBy('wins', 'desc')
//           .limit(10)
//           .get()
//           .then(function(querySnapshot) {
//               var leaderboard = [];
//               querySnapshot.forEach(function(doc) {
//                   leaderboard.push(doc.data());
//               });
//               var leaderboardJson = JSON.stringify({ players: leaderboard });
              
//               // Wait for SendMessage to be defined before calling it.
//               var attempts = 0;
//               var interval = setInterval(function() {
//                   if (typeof SendMessage === "function") {
//                       clearInterval(interval);
//                       callSendMessage(leaderboardJson);
//                   } else {
//                       attempts++;
//                       if (attempts > 20) { // wait up to about 2 seconds (if interval is 100ms)
//                           clearInterval(interval);
//                           console.error("SendMessage is still not defined after waiting.");
//                       }
//                   }
//               }, 100);
//           })
//           .catch(function(error) {
//               console.error("Error fetching leaderboard: ", error);
//           });
//     };
// })();
