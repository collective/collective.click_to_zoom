// click-to-zoom.js
document.addEventListener("DOMContentLoaded", function() {
    var scale = 1;
    var pointX = 0;
    var pointY = 0;
    var startX = 0;
    var startY = 0;
    var isDragging = false;
    var dragStarted = false;

    // Create the Lightbox element and insert it into the DOM
    var lightbox = document.createElement('div');
    lightbox.id = 'click-to-zoom-lightbox';
    lightbox.style.display = 'none';
    
    var img = document.createElement('img');
    img.draggable = false;
    
    var closeBtn = document.createElement('span');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '&times;';
    
    lightbox.appendChild(img);
    lightbox.appendChild(closeBtn);
    document.body.appendChild(lightbox);

    function updateTransform() {
        img.style.transform = 'translate(' + pointX + 'px, ' + pointY + 'px) scale(' + scale + ')';
    }

    function resetLightbox() {
        scale = 1;
        pointX = 0;
        pointY = 0;
        updateTransform();
        lightbox.classList.remove('zoomed');
        lightbox.classList.remove('active');
        setTimeout(function() {
            if (!lightbox.classList.contains('active')) {
                lightbox.style.display = 'none';
            }
        }, 300);
    }

    // Lightbox close logic
    lightbox.addEventListener('click', function(e) {
        if (e.target !== img && !dragStarted) {
            resetLightbox();
        }
    });

    closeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        resetLightbox();
    });

    // Zoom on click
    img.addEventListener('click', function(e) {
        e.stopPropagation();
        if (dragStarted) {
            dragStarted = false;
            return;
        }

        if (scale > 1) {
            scale = 1;
            pointX = 0;
            pointY = 0;
            lightbox.classList.remove('zoomed');
        } else {
            scale = 2.5;
            lightbox.classList.add('zoomed');
        }
        updateTransform();
    });

    // Zoom on wheel
    lightbox.addEventListener('wheel', function(e) {
        e.preventDefault();
        var delta = -e.deltaY;
        var factor = 0.2;
        var newScale = scale + (delta > 0 ? factor : -factor);

        if (newScale >= 1 && newScale <= 10) {
            // Zoom towards cursor
            var rect = img.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            
            pointX -= (x - rect.width / 2) * (newScale / scale - 1);
            pointY -= (y - rect.height / 2) * (newScale / scale - 1);
            
            scale = newScale;
            if (scale > 1) {
                lightbox.classList.add('zoomed');
            } else {
                lightbox.classList.remove('zoomed');
                pointX = 0;
                pointY = 0;
            }
            updateTransform();
        }
    }, { passive: false });

    // Drag to pan
    img.addEventListener('pointerdown', function(e) {
        if (scale <= 1) return;
        isDragging = true;
        dragStarted = false;
        startX = e.clientX - pointX;
        startY = e.clientY - pointY;
        img.setPointerCapture(e.pointerId);
    });

    img.addEventListener('pointermove', function(e) {
        if (!isDragging) return;
        
        var newPointX = e.clientX - startX;
        var newPointY = e.clientY - startY;

        // Determine if we've moved enough to call it a drag
        if (Math.abs(newPointX - pointX) > 2 || Math.abs(newPointY - pointY) > 2) {
            dragStarted = true;
            lightbox.classList.add('dragging');
        }

        pointX = newPointX;
        pointY = newPointY;
        updateTransform();
    });

    img.addEventListener('pointerup', function(e) {
        if (!isDragging) return;
        isDragging = false;
        lightbox.classList.remove('dragging');
        img.releasePointerCapture(e.pointerId);
    });

    // Find links and initialize
    var zoomLinks = document.querySelectorAll('a.click-to-zoom');
    
    zoomLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            var imageSrc = this.getAttribute('href');
            if (imageSrc) {
                img.src = imageSrc;
                scale = 1;
                pointX = 0;
                pointY = 0;
                updateTransform();
                lightbox.style.display = 'flex';
                setTimeout(function() {
                    lightbox.classList.add('active');
                }, 10);
            }
        });
    });
});
