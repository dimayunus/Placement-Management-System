document.addEventListener("DOMContentLoaded", function() {

    const toggleIcon = document.getElementById("sidebar-toggle");
    const sidebar = document.getElementById("sidebar");

    toggleIcon.addEventListener("click", function() {
        sidebar.classList.toggle("active");
    });
    
    // Function to fetch company names from the server
    function fetchCompanyNames() {
        fetch("/company_names")
            .then(response => response.json())
            .then(data => {
                // Clear existing options
                const companyNameDropdown = document.getElementById("company-name");
                companyNameDropdown.innerHTML = "";
                
                // Add default option
                const defaultOption = document.createElement("option");
                defaultOption.text = "Select Company";
                defaultOption.disabled = true;
                defaultOption.selected = true;
                companyNameDropdown.add(defaultOption);
                
                // Add options for each company name
                data.forEach(companyName => {
                    const option = document.createElement("option");
                    option.text = companyName;
                    companyNameDropdown.add(option);
                });
            })
            .catch(error => console.error("Error fetching company names:", error));
    }
    
    // Call fetchCompanyNames function to populate the dropdown menu
    fetchCompanyNames();
});
