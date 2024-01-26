
const fetchData = async (url, id = undefined) => {
    try {
        // Append query parameters to the URL if 'id' is provided
        const fullUrl = id !== undefined ? `${url}/${id}` : url;
        const response = await fetch(fullUrl);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log(data); 
        const campaigns = data.data;
        console.log(campaigns)
        // Select the existing HTML element for the campaign list
        const campaignList = document.getElementById('campaignList');

        // Loop through each campaign and create elements dynamically
        campaigns.forEach(campaign => {
            const campaignItem = document.createElement('div');
            campaignItem.className = 'campaign';

            // Create HTML content for each campaign
            const content = `
                <img class="campaignImage" src="${campaign.imageURL}" alt="Campaign Image">
                <h4 class="campaignName">${campaign.title}</h4>
                <p class="campaignDescription">${campaign.description}</p>
            `;

            campaignItem.innerHTML = content;

            // Append each campaign item to the campaign list
            campaignList.appendChild(campaignItem);
        });

    } catch (error) {
        console.error('Error:', error);
    }
};

fetchData("http://127.0.0.1:5000/api/v1/campaigns/")
