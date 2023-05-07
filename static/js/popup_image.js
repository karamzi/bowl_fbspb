// Get the modal
const modal = document.getElementById("myModal")
console.log('re')

// Get the image and insert it inside the modal - use its "alt" text as a caption
const images = document.querySelectorAll('.myImage')
const modalImg = document.getElementById("img01")
const captionText = document.getElementById("caption")

images.forEach(image => {
    image.addEventListener('click', () => {
        modal.style.display = "block"
        modalImg.src = image.src
        captionText.innerHTML = image.alt
    })
})

// Get the <span> element that closes the modal
const span = document.getElementsByClassName("close")[0]

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none"
}

modal.onclick = function() {
  modal.style.display = "none"
}
