// index.js
// Main JS file for Instrument Manager

// Query Instrument
function query(id, query)
{
    fetch(`./api/instrument/${id}/${query}`)
        .then((response) => { 
            if(response.status != 200){
                alert(response.statusText);
            } else {
                response.json().then((data) => {
                    alert(data);
                });
            }
        }).catch((error) => {
            alert(error);
        });
}