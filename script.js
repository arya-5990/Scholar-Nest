function navigate(section) {
    if (section === "logout") {
        logoutUser();
    } else if (section === "login") {
        window.location.href = "login.html"; // Redirect to login page
    } else {
        window.location.href = "#"; // Placeholder for other links
    }
}

function navigateTo(page) {
    window.location.href = page;
}


function logoutUser() {
    localStorage.removeItem("user"); // Remove stored user data
    alert("You have been logged out.");
    window.location.href = "login.html"; // Redirect to login page
}

document.addEventListener("DOMContentLoaded", function () {
    let user = JSON.parse(localStorage.getItem("user")); // Get user data from localStorage
    let profileMenu = document.getElementById("profileMenu");
    let loginButton = document.getElementById("loginButton");

    if (user && user.isLoggedIn) {
        profileMenu.style.display = "inline-block"; // Show profile menu if user is logged in
        loginButton.style.display = "none"; // Hide login button
    } else {
        profileMenu.style.display = "none"; // Hide profile menu
        loginButton.style.display = "inline-block"; // Show login button
    }
});


document.getElementById("upload-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("subject", document.getElementById("subject").value);
    formData.append("semester", document.getElementById("semester").value);
    formData.append("course", document.getElementById("course").value);
    formData.append("file", document.getElementById("file").files[0]);

    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
        credentials: "include"  // Ensures session-based authentication
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById("upload-form").reset();
    })
    .catch(error => console.error("Error:", error));
});
document.getElementById("fetch-uploads").addEventListener("click", function () {
    fetch("http://127.0.0.1:5000/my_uploads", { credentials: "include" })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            let uploadsList = document.getElementById("uploads-list");
            uploadsList.innerHTML = "";

            if (Array.isArray(data.uploads) && data.uploads.length > 0) {
                data.uploads.forEach(resource => {
                    let li = document.createElement("li");
                    li.innerHTML = `${resource.name} - <a href="http://127.0.0.1:5000${resource.file_url}" target="_blank">Download</a>`;
                    uploadsList.appendChild(li);
                });
            } else {
                uploadsList.innerHTML = "<li>No uploads found</li>";
            }
        })
        .catch(error => console.error("Error:", error));
});







function updateSubjects() {
    let course = document.getElementById('course').value;
    let semester = document.getElementById('semester').value;
    let subjectDropdown = document.getElementById('subject');

    subjectDropdown.innerHTML = '<option value="" disabled selected>Select Subject</option>';

    if (course && semester) {
        let selectedSubjects = subjects[course][semester] || [];
        selectedSubjects.forEach(subject => {
            let option = document.createElement('option');
            option.value = subject;
            option.textContent = subject;
            subjectDropdown.appendChild(option);
        });
    }
}
