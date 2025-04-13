document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_user_info")
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("user-name").value = data.username;
                document.querySelector(".profile p strong").textContent = `Name: ${data.username}`;
                document.getElementById("dashboard-username").textContent = data.username;
            }
        })
        .catch(error => console.error("Error fetching user info:", error));
});

// Toggle Profile Section
document.querySelector('.sidebar h3').addEventListener('click', () => {
    const profile = document.querySelector('.profile');
    profile.style.display = profile.style.display === 'block' ? 'none' : 'block';
});

// Toggle Semester, Course, and Unit Sections
document.querySelectorAll('.semester, .course, .unit').forEach(item => {
    item.addEventListener('click', (e) => {
        e.stopPropagation();
        const nextLevel = item.querySelector('.courses, .units, .pdfs');
        if (nextLevel) {
            nextLevel.style.display = nextLevel.style.display === 'block' ? 'none' : 'block';

            // Scroll to the newly opened content
            setTimeout(() => {
                nextLevel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 200); // Adjust the delay as needed for smoother scrolling
        }
    });
});

// Update Profile Function
function updateProfile(role) {
    const name = document.getElementById(`${role}-name`).value;
    const password = document.getElementById(`${role}-password`).value;
    
    fetch("/update_profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: name, password: password })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error("Error updating profile:", error));
}
