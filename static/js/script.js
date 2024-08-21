function redirectToStudentLogin() {
    window.location.href='/student-login';
}

function redirectToFacultyLogin() {
    window.location.href='/faculty-login';
}

document.addEventListener("DOMContentLoaded", function() {
    const toggleIcon = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    toggleIcon.addEventListener("click", function() {
        sidebar.classList.toggle("active");
    });
});