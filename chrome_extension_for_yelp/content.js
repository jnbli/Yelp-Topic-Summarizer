// Inform the background page that 
// this tab should have a page-action.
chrome.runtime.sendMessage({
  from: 'content',
  subject: 'showPageAction',
});

// Listen for messages from the popup.
chrome.runtime.onMessage.addListener((msg, sender, response) => {
  // First, validate the message's structure.
  if ((msg.from === 'popup') && (msg.subject === 'DOMInfo')) {

    // Collect the necessary data. 
    // (For your specific requirements `document.querySelectorAll(...)`
    //  should be equivalent to jquery's `$(...)`.)

    var url = document.URL.split('?')[0];
    var numPages = 1;
    span = document.querySelectorAll('section > div > div > div > div > span');
    for (i=0; i<span.length; i++) {
      match = span[i].textContent.match(/(\d+) of (\d+)/)
      if (match) {
        numPages = match[2];
        break
      }
    }

    var domInfo = {
      url: url,
      numPages: numPages
    };

    // Directly respond to the sender (popup), 
    // through the specified callback.
    response(domInfo);

  }
});