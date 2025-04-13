// admin_dashboard.js

document.addEventListener('DOMContentLoaded', () => {
    // Toggle sidebar profile
    document.querySelector('.sidebar h3').addEventListener('click', () => {
        const profile = document.querySelector('.profile');
        profile.style.display = profile.style.display === 'block' ? 'none' : 'block';
    });

    // Toggle semester visibility
    document.querySelectorAll('.semester').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const courses = item.querySelector('.courses');
            if (courses) {
                courses.style.display = courses.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Toggle course visibility
    document.querySelectorAll('.course').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const units = item.querySelector('.units');
            if (units) {
                units.style.display = units.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Toggle unit visibility
    document.querySelectorAll('.unit').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const pdfs = item.querySelector('.pdfs');
            const managePdfs = item.querySelector('.manage-pdfs');
            if (pdfs && managePdfs) {
                pdfs.style.display = pdfs.style.display === 'block' ? 'none' : 'block';
                managePdfs.style.display = managePdfs.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    // Add PDF functionality
    document.querySelectorAll('.add-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent collapse
            const managePdfs = btn.closest('.manage-pdfs');
            const fileInput = managePdfs.querySelector('input[type="file"]');
            const unit = fileInput.getAttribute('data-unit');
            const courseCode = fileInput.getAttribute('data-course');
            const file = fileInput.files[0];
            const messageSpan = managePdfs.querySelector('.upload-message');

            if (!file) {
                messageSpan.textContent = "Please select a PDF file.";
                messageSpan.style.color = 'red';
                return;
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("course_code", courseCode);
            formData.append("unit_number", unit);

            fetch("/upload_pdf", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    const pdfLink = managePdfs.previousElementSibling.querySelector('a');
                    pdfLink.textContent = file.name;
                    pdfLink.setAttribute('data-pdf', file.name);
                    pdfLink.setAttribute('href', `/static/uploads/${file.name}`);
                    messageSpan.textContent = `PDF uploaded for Unit ${unit}`;
                    messageSpan.style.color = 'green';
                } else {
                    messageSpan.textContent = `Upload failed: ${data.message}`;
                    messageSpan.style.color = 'red';
                    if (data.message === "Unauthorized") {
                        window.location.href = "/login.html";
                    }
                }
            })
            .catch(err => {
                messageSpan.textContent = `Error: ${err}`;
                messageSpan.style.color = 'red';
            });
        });
    });

    // Modify PDF functionality (reuses add logic)
    document.querySelectorAll('.modify-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const managePdfs = btn.closest('.manage-pdfs');
            const addBtn = managePdfs.querySelector('.add-btn');
            addBtn.click(); // Trigger addPDF logic
        });
    });

    // Delete PDF functionality
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const managePdfs = btn.closest('.manage-pdfs');
            const pdfLink = managePdfs.previousElementSibling.querySelector('a');
            const unit = pdfLink.closest('.unit').textContent.trim().split('\n')[0];
            pdfLink.textContent = 'No PDF available';
            pdfLink.removeAttribute('href');
            pdfLink.removeAttribute('data-pdf');
            managePdfs.querySelector('.upload-message').textContent = `Deleted PDF for ${unit}`;
            managePdfs.querySelector('.upload-message').style.color = 'red';
        });
    });

    // Update profile functionality
    window.updateProfile = function(role) {
        const name = document.getElementById(`${role}-name`).value;
        const password = document.getElementById(`${role}-password`).value;
        if (name.trim() || password.trim()) {
            alert(`Profile updated - Name: ${name}, ${password ? 'Password changed' : 'No password change'}`);
            // Optionally send to server via fetch if you add an endpoint
        }
    };
});