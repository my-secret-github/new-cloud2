function box_id(id) {
    return `guide_id_${id}`;
}

// Combined event listener for 'submitBtn'
document.getElementById("submitBtn").addEventListener("click", function(event) {
    event.preventDefault();

    var button = this;
    button.classList.remove('loaded');
    button.classList.add('loading');
    button.disabled = true;

    let foundCheckboxes = [];

    // Loop through the IDs and collect the ones that exist
    for (let i = 1; i <= 200; i++) {
        const checkbox = document.getElementById(box_id(i));
        if (checkbox) {
            foundCheckboxes.push(box_id(i));
        }
    }

    let checkedguides = [];

    // Loop over found checkboxes and check which ones are checked
    for (let i = 0; i < foundCheckboxes.length; i++) {
        const checkbox = document.getElementById(foundCheckboxes[i]);
        if (checkbox && checkbox.checked) {
            checkedguides.push(foundCheckboxes[i]);
        }
    }

    const fName = document.getElementById("inputText");
    const fNameText = fName ? fName.value.trim() : '';

    if (!fNameText) {
        alert("Name box is empty! Please enter a name.");
        button.disabled = false;
        button.classList.remove('loading');
        return;
    }

    const style = document.getElementById("inputStyle");
    const styleText = style ? style.value.trim() : '';

    if (!styleText) {
        alert("Please Select a 3 letter style!");
        button.disabled = false;
        button.classList.remove('loading');
        return;
    }

    if (checkedguides.length === 0) {
        alert("No guides selected! Select a guide before making a PDF.");
        button.disabled = false;
        button.classList.remove('loading');
        return;
    }

    // Post the checked checkboxes to the server
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'data': checkedguides, 'style': styleText, 'fName': fNameText }),
    })
    .then(response => response.json())
    .then(data => {
        window.open(data, "_blank");
        alert(`Pdf has been made at ${data}`);
        // Reset the button text and state
        button.disabled = false;
        button.classList.remove('loading');
        button.classList.add('loaded');
    })
    .catch((error) => {
        console.error('Error:', error);
        button.disabled = false;
        button.classList.remove('loading');
    });

    // Clear any existing intervals to avoid overlap
    if (button.intervalId) {
        clearInterval(button.intervalId);
    }

    // Start progress check
    button.intervalId = setInterval(function() {
        fetch('/get_progress')
            .then(response => response.json())
            .then(data => {
                var percentage = data.progress;
                button.textContent = 'Loading ' + percentage;

                if (Number(percentage) === 100) {
                    clearInterval(button.intervalId);
                    button.intervalId = null;  // Clear the intervalId after completion
                    button.textContent = 'Pdf Complete';
                    button.disabled = false;
                    button.classList.remove('loading');
                    button.classList.add('loaded');
                }
            })
            .catch(error => {
                console.error('Error fetching progress:', error);
                clearInterval(button.intervalId);  // Clear the interval in case of an error
                button.disabled = false;
                button.classList.remove('loading');
            });
    }, 500);
});
