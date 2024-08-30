
document.getElementById("submitQaBtn").addEventListener("click", function(event) {
    this.classList.remove('loaded')    
    this.classList.add('loading')
    event.preventDefault();
    let foundCheckboxes = [];
    console.log(this.classList)


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

    const fName = document.getElementById("inputText")
    const fNameText = fName ? fName.value.trim() : '';

    if (!fNameText) {
        alert("Name box is empty! Please enter a name.");
        return;
    }

    const style = document.getElementById("inputStyle")
    const styleText = style ? style.value.trim() : '';

    if (!styleText)
        alert("Please Select a 3 letter style!")

    if (checkedguides.length === 0) {
        alert("No guides selected! Select a guide before making a PDF.")
        return
    }


        // Post the checked checkboxes to the server
        fetch('/processQa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'data': checkedguides, 'fName': fNameText, 'style': styleText}),

        })
        .then(response => response.json())
        .then(data => {
            window.open(data, "_blank");
            alert(`QA Pdf has been made at ${data}`)
            //console.log('Success:', data);
        })
        .catch((error) => {
            //console.error('Error:', error);
        });
}
)