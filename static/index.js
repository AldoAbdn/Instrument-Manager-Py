// index.js
// Main JS file for Instrument Manager

window.onload = (event) => {
    if(window.location.pathname == "/"){
        removeToken();
        sessionStorage.setItem("loggedIn", false);
    } else {
        let loggedIn = sessionStorage.getItem("loggedIn");
        if(loggedIn == "false"){
            logout();
        }
    }
}

function keypadPress(key) 
{
    let input = document.getElementById('Code');
    if(key != '#'){
        input.value += key;
    } else { // Submit passcode
        authenticate(input.value);
    }
}

function authenticate(passcode)
{
    let http = new XMLHttpRequest();
    http.open("POST", "/authenticate", true);
    http.setRequestHeader('Content-type', 'application/json');
    http.onreadystatechange = function()
    {
        if(http.readyState = 4 && http.status >= 400){
            showmodal("Error", "Incorrect Passcode");
        }else if(http.readyState = 4 && http.status == 200){
            let response = JSON.parse(http.response);
            if (response.login)
                window.location.assign("/instrumentmanager");
            sessionStorage.setItem("loggedIn", true);
        }
    }
    params = {username: "Admin", password: passcode};
    http.send(JSON.stringify(params));
}

function logout(){
    removeToken();
    sessionStorage.setItem("loggedIn", false);
    window.location.replace("/");
}

function removeToken(){
    let http = new XMLHttpRequest();
    http.open("POST", "/token/remove", true);
    http.send(null);
}

function deleteKey() 
{
    let input = document.getElementById('Code');
    let text = input.value;
    if(text != ""){
        input.value = text.slice(0, -1);
    }
}

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