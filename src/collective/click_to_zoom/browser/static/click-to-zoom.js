// click-to-zoom.js
document.addEventListener("DOMContentLoaded", function() {
    var scale = 1;
    var pointX = 0;
    var pointY = 0;
    var startX = 0;
    var startY = 0;
    var isDragging = false;
    var dragStarted = false;
    var maxScale = 1;
    var originalWidth = 0;
    var originalHeight = 0;

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

    function applyBoundaries(x, y, s) {
        var vW = lightbox.offsetWidth;
        var vH = lightbox.offsetHeight;
        var imgW = img.offsetWidth * s;
        var imgH = img.offsetHeight * s;

        // Limit panning so at least 1/4 of the image is always visible
        var limitX = vW / 2 + imgW / 4;
        var limitY = vH / 2 + imgH / 4;

        if (Math.abs(x) > limitX) x = (x > 0 ? 1 : -1) * limitX;
        if (Math.abs(y) > limitY) y = (y > 0 ? 1 : -1) * limitY;

        return { x: x, y: y };
    }

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
        lightbox.classList.remove('not-zoomable');
        document.body.style.overflow = '';
        setTimeout(function() {
            if (!lightbox.classList.contains('active')) {
                lightbox.style.display = 'none';
            }
        }, 300);
    }

    function calculateMaxScale() {
        if (originalWidth > 0) {
            // Wait for image to be rendered to get its actual displayed size at scale 1
            var displayedWidth = img.offsetWidth;
            if (displayedWidth > 0) {
                maxScale = originalWidth / displayedWidth;
            } else {
                maxScale = 1;
            }
        } else {
            maxScale = 10; // Fallback if dimensions not provided
        }

        if (maxScale <= 1.01) { // 1.01 to account for minor rounding
            lightbox.classList.add('not-zoomable');
            maxScale = 1;
        } else {
            lightbox.classList.remove('not-zoomable');
        }
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

        if (maxScale <= 1) return;

        if (scale > 1) {
            scale = 1;
            pointX = 0;
            pointY = 0;
            lightbox.classList.remove('zoomed');
        } else {
            scale = maxScale;
            lightbox.classList.add('zoomed');
        }
        updateTransform();
    });

    // Zoom on wheel
    lightbox.addEventListener('wheel', function(e) {
        e.preventDefault();
        if (maxScale <= 1) return;
        
        var delta = -e.deltaY;
        var factor = 0.2;
        var newScale = scale + (delta > 0 ? factor : -factor);

        // Clamp scale
        if (newScale > maxScale) newScale = maxScale;
        if (newScale < 1) newScale = 1;

        if (newScale !== scale) {
            // Zoom towards cursor
            var rect = img.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            
            var newPointX = pointX - (x - rect.width / 2) * (newScale / scale - 1);
            var newPointY = pointY - (y - rect.height / 2) * (newScale / scale - 1);
            
            scale = newScale;
            if (scale > 1.01) {
                lightbox.classList.add('zoomed');
                // Apply boundaries
                var bounded = applyBoundaries(newPointX, newPointY, scale);
                pointX = bounded.x;
                pointY = bounded.y;
            } else {
                scale = 1;
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

        // Constraints: prevent dragging the image completely out of view
        var bounded = applyBoundaries(newPointX, newPointY, scale);
        newPointX = bounded.x;
        newPointY = bounded.y;

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
            originalWidth = parseInt(this.getAttribute('data-width') || 0);
            originalHeight = parseInt(this.getAttribute('data-height') || 0);

            if (imageSrc) {
                img.src = imageSrc;
                scale = 1;
                pointX = 0;
                pointY = 0;
                updateTransform();
                lightbox.style.display = 'flex';
                document.body.style.overflow = 'hidden';
                
                // We need to wait for the image to be potentially loaded or at least have dimensions
                if (img.complete) {
                    calculateMaxScale();
                } else {
                    img.onload = function() {
                        calculateMaxScale();
                        img.onload = null;
                    };
                }

                setTimeout(function() {
                    lightbox.classList.add('active');
                }, 10);
            }
        });
    });
});
