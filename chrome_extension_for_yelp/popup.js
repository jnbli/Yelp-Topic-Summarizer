// Update the relevant fields with the new data.
// const setDOMInfo = info => {
//   document.getElementById('reviews').textContent = info.url + info.numPages;
// };

function turnOrange() {
  topics = document.getElementsByClassName('topic')
  console.log(topics)
  for (i=0; i<topics.length; i++) {
    topics[i].style.background = '';
  }
  hides = document.getElementsByClassName('hide')
  for (i=0; i<hides.length; i++) {
    hides[i].style.display = 'none';
  }

  this.style.background = 'gray';
  hide = document.getElementById(this.id + 'text')
  hide.style.display = 'block'
}


function setDOMInfo(info) {
  // document.getElementById('reviews').textContent = info;
  info = JSON.parse(info)
  data = info.data
  
  document.getElementById('loading').style.display = 'none';
  document.getElementById('loadicon').style.display = 'none';
  document.getElementById('newdiv').style.display = 'block';

  buttons = []
  divs = []
  for (topic in data) {
    button = document.createElement('button')
    button.innerText = topic
    button.classList = ['topic']
    buttons.push(button)
    

    div = document.createElement('div')
    div.innerText = data[topic]
    div.classList = ['hide']
    divs.push(div)
  }
    


  for (i=0; i<buttons.length; i++) {
    buttons[i].id = 'topic'+i
    buttons[i].onclick = function () {turnOrange.call(this)}
    divs[i].id = 'topic'+i+'text'
  }

  for (i=0; i<buttons.length; i++) {
    document.body.append(buttons[i])
  }

  for (i=0; i<divs.length; i++) {
    document.body.append(divs[i])
  }


}

function askBert(info) {
  // document.getElementById('reviews').textContent = 'loading...';

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
       if (this.readyState == 4 && this.status == 200) {
           setDOMInfo(this.responseText);
       }
  };
  xhttp.open("POST", "http://127.0.0.1:5000/topics", true);
  xhttp.setRequestHeader("Content-type", "application/json");
  xhttp.send(JSON.stringify({"url": info.url, "numPages": Math.min(info.numPages, 5)}));
}


// Once the DOM is ready...
window.addEventListener('DOMContentLoaded', () => {
  // ...query for the active tab...
  chrome.tabs.query({
    active: true,
    currentWindow: true
  }, tabs => {
    // ...and send a request for the DOM info...
    chrome.tabs.sendMessage(
        tabs[0].id,
        {from: 'popup', subject: 'DOMInfo'},
        // ...also specifying a callback to be called 
        //    from the receiving end (content script).
        askBert);
  });
});


