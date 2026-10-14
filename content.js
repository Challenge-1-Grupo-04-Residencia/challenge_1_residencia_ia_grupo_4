if (!window.__veraContentScriptInstalled) {
  window.__veraContentScriptInstalled = true;

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type !== "VERA_GET_PAGE_TEXT") {
      return;
    }

    sendResponse({
      title: document.title,
      url: window.location.href,
      text: document.body?.innerText ?? ""
    });
  });
}