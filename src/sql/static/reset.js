document.getElementById("reset").addEventListener("click", function() {
    console.log("hello")
    for (let i = 1; i <= 200; i++) {
        const checkbox = document.getElementById(box_id(i));
        if (checkbox) {
            checkbox.checked = false
        }

    }

    input_name = document.getElementById("inputText")
    input_style = document.getElementById("inputStyle")

    input_name.value = ""
    input_style.value = ""
})