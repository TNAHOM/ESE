console.log('hi')
function handleDrop(event) {
  event.preventDefault();
  
  var files = event.dataTransfer.files;
  var formData = new FormData();

  for (var i = 0; i < files.length; i++) {
    formData.append('file', files[i]);
  }

  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);

  xhr.onload = function () {
    if (xhr.status === 200) {
      console.log(xhr.responseText);
    }
  };

  xhr.send(formData);
}

function handleDragOver(event) {
  event.preventDefault();
}
