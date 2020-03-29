
function el( id ) {
    return document.getElementById( id );
}

function by_class( klass ) {
    return document.getElementsByClassName(klass);
}


function openTab(tabName) {
  let tabs = by_class("tab");
  for( tab of tabs ) {
    tab.style.display = "none";
  }

  let tablinks = by_class("tablink");
  for( tablink of tablinks ) {
    console.log
    tablink.className = tablink.className.replace(" active", "");
  }

  console.log(`openTab (${tabName})`)
  el(tabName).style.display = "block";
  event.currentTarget.className += " active";
}
