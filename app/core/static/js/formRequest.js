
const submitForm = (url, id) => {
    // Get form data
    const formData = new FormData(document.getElementById(id));

    // Fetch API
    fetch(url, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json(); // or response.text() depending on your server response
    })
    .then(data => {
        // Handle the response data
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


    
