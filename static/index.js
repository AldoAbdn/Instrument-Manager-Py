// index.js
// Main JS file for Instrument Manager

// Query Instrument
function query(id, query)
{
    var buttons = document.getElementsByClassName(`${id}-button`);
    for(var button of buttons){
        button.setAttribute("disabled", "disabled");
    }
    fetch(`./api/instrument/${id}?query=${query}`)
        .then((response) => { 
            if(response.status != 200){
                showmodal("Error", response.statusText);
            } else {
                response.json().then((data) => {
                    showmodal(`Result for query ${query} on ${id}`, `${data.result}`);
                });
            }
            for(var button of buttons){
                button.removeAttribute("disabled");
            }
        }).catch((error) => {
            showmodal("Error", error);
            for(var button of buttons){
                button.removeAttribute("disabled");
            }
        });
}

function showmodal(title, content){
    var modal = document.getElementById("modal");
    var modalTitle = document.getElementById("title");
    var modalContent = document.getElementById("content");
    var closeButton = document.getElementById("closeButton");
    modalTitle.innerText = title;
    modalContent.innerText = content;
    modal.style.display = "block";
    window.setTimeout(function() {
        closeButton.focus();
    });
}

function hidemodal(){
    var modal = document.getElementById("modal");
    modal.style.display = "none";
    location.reload();
}