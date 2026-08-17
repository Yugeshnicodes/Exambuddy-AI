// =========================================================
// FIREBASE CONFIGURATION
// =========================================================

const firebaseConfig = {

    apiKey:
        "AIzaSyA3HJGY33W_JNiGW_J0CJcKMyeaFE2pyqE",

    authDomain:
        "exam-buddy-ai.firebaseapp.com",

    projectId:
        "exam-buddy-ai",

    storageBucket:
        "exam-buddy-ai.firebasestorage.app",

    messagingSenderId:
        "662182848112",

    appId:
        "1:662182848112:web:6970edbe8de7f3e76536b5",

    measurementId:
        "G-1T08HCS2XG"
};


// =========================================================
// INITIALIZE FIREBASE
// =========================================================

firebase.initializeApp(firebaseConfig);

const auth =
    firebase.auth();


// =========================================================
// HTML ELEMENTS
// =========================================================

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

const message =
    document.getElementById("message");


// =========================================================
// CREATE ACCOUNT
// =========================================================

async function createAccount() {

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value.trim();


    if (!email || !password) {

        message.textContent =
            "Enter email and password first.";

        return;
    }


    if (password.length < 6) {

        message.textContent =
            "Password must contain at least 6 characters.";

        return;
    }


    try {

        message.textContent =
            "Creating account...";


        const result =
            await auth.createUserWithEmailAndPassword(
                email,
                password
            );


        console.log(
            "Account created:",
            result.user.email
        );


        message.textContent =
            "Account created successfully!";


        setTimeout(function () {

            window.location.href = "/chat";

        }, 1000);


    } catch (error) {

        console.error(
            "Create Account Error:",
            error
        );


        message.textContent =
            getFirebaseError(error);
    }
}


// =========================================================
// LOGIN
// =========================================================

async function loginUser() {

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value.trim();


    if (!email || !password) {

        message.textContent =
            "Enter email and password first.";

        return;
    }


    try {

        message.textContent =
            "Logging in...";


        const result =
            await auth.signInWithEmailAndPassword(
                email,
                password
            );


        console.log(
            "Login successful:",
            result.user.email
        );


        message.textContent =
            "Login successful!";


        setTimeout(function () {

            window.location.href = "/chat";

        }, 500);


    } catch (error) {

        console.error(
            "Login Error:",
            error
        );


        message.textContent =
            getFirebaseError(error);
    }
}


// =========================================================
// FORGOT PASSWORD
// =========================================================

async function resetPassword() {

    const email =
        emailInput.value.trim();


    if (!email) {

        message.textContent =
            "Enter your email first.";

        return;
    }


    try {

        message.textContent =
            "Sending password reset email...";


        await auth.sendPasswordResetEmail(
            email
        );


        message.textContent =
            "Password reset email sent. Check your email.";


    } catch (error) {

        console.error(
            "Password Reset Error:",
            error
        );


        message.textContent =
            getFirebaseError(error);
    }
}


// =========================================================
// FIREBASE ERROR MESSAGES
// =========================================================

function getFirebaseError(error) {

    switch (error.code) {

        case "auth/email-already-in-use":

            return "This email is already registered. Please login.";

        case "auth/invalid-email":

            return "Please enter a valid email address.";

        case "auth/weak-password":

            return "Password must contain at least 6 characters.";

        case "auth/invalid-credential":

            return "Incorrect email or password.";

        case "auth/user-not-found":

            return "Account not found. Please create an account.";

        case "auth/wrong-password":

            return "Incorrect password.";

        case "auth/too-many-requests":

            return "Too many attempts. Please try again later.";

        default:

            return (
                error.message ||
                "Unable to complete the request."
            );
    }
}