document.addEventListener("DOMContentLoaded", function () {
    let form = document.getElementById("Form");
    
    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            let username = document.getElementById("username").value.trim();
            let password = document.getElementById("password").value.trim();

            if (!username || !password) {
                alert("Please enter both username and password.");
                return;
            }

            // Use a data attribute from the form to determine login type (more reliable)
            let loginType = form.dataset.type; // 'user' or 'admin'

            try {
                let response = await fetch(loginType === 'admin' ? "/admin_login" : "/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                let data = await response.json();

                if (data.success) {
                    if (data.role === "admin") {
                        window.location.href = "/admin_dashboard";
                    } else if (data.role === "user") {
                        window.location.href = "/dashboard";
                    } else {
                        alert("Unexpected role. Contact support.");
                    }
                } else {
                    alert(data.message || "Invalid credentials. Try again.");
                }
            } catch (error) {
                console.error("Login error:", error);
                alert("An error occurred. Please try again later.");
            }
        });
    } else {
        console.error("Login form not found!");
    }
});
