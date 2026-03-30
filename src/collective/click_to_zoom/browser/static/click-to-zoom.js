// click-to-zoom.js
document.addEventListener("DOMContentLoaded", function() {
    // Create the Lightbox element and insert it into the DOM
    var lightbox = document.createElement('div');
    lightbox.id = 'click-to-zoom-lightbox';
    lightbox.style.display = 'none';
    
    var img = document.createElement('img');
    var closeBtn = document.createElement('span');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '&times;';
    
    lightbox.appendChild(img);
    lightbox.appendChild(closeBtn);
    document.body.appendChild(lightbox);
    
    // Lightbox close logic
    lightbox.addEventListener('click', function(e) {
        if (e.target !== img) {
            lightbox.classList.remove('active');
            setTimeout(function() {
                lightbox.style.display = 'none';
            }, 300); // Wait matches the CSS transition duration
        }
    });

    // Find links with zoom applied
    var zoomLinks = document.querySelectorAll('a.click-to-zoom');
    
    zoomLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            var imageSrc = this.getAttribute('href');
            if (imageSrc) {
                img.src = imageSrc;
                lightbox.style.display = 'flex';
                // Wait slightly before adding the class so the transition triggers
                setTimeout(function() {
                    lightbox.classList.add('active');
                }, 10);
            }
        });
    });
});
