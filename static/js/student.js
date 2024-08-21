document.addEventListener("DOMContentLoaded", function() {
    // Function to toggle sidebar
    const toggleButton = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    toggleButton.addEventListener("click", function() {
        sidebar.classList.toggle("active");
    });

    
});
