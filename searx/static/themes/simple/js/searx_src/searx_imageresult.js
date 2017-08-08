/**
*
* Google Image Layout v0.0.1
* Description, by Anh Trinh.
* Heavily modified for searx
* http://trinhtrunganh.com
*
* @license Free to use under the MIT License.
*
*/
(function(w, d) {
  'use strict';
  
  function ImageLayout(container_selector, results_selector, img_selector, maxHeight) {
    this.container_selector = container_selector;
    this.results_selector = results_selector;
    this.img_selector = img_selector;
    this.margin = 10;
    this.maxHeight = maxHeight;
    this._alignAllDone = true;
  }

  /**
  * Get the height that make all images fit the container
  *
  * width = w1 + w2 + w3 + ... = r1*h + r2*h + r3*h + ...
  *
  * @param  {[type]} images the images to be calculated
  * @param  {[type]} width  the container witdth
  * @param  {[type]} margin the margin between each image
  *
  * @return {[type]}        the height
  */
  ImageLayout.prototype._getHeigth = function(images, width) {
    var r = 0,
    img;

    width -= images.length * this.margin;
    for (var i = 0; i < images.length; i++) {
      img = images[i];
      if ((img.naturalWidth > 0) && (img.naturalHeight > 0)) {
        r += img.naturalWidth / img.naturalHeight;
      } else {
        // assume that not loaded images are square
        r += 1;
      }
    }

    return width / r; //have to round down because Firefox will automatically roundup value with number of decimals > 3
  };

  ImageLayout.prototype._setSize = function(images, height) {
    var img, imgWidth, imagesLength = images.length;
    for (var i = 0; i < imagesLength; i++) {
      img = images[i];
      if ((img.naturalWidth > 0) && (img.naturalHeight > 0)) {
        imgWidth = height * img.naturalWidth / img.naturalHeight;
      } else {
        // not loaded image : make it square as _getHeigth said it
        imgWidth = height;
      }
      img.style.width = imgWidth + 'px';
      img.style.height = height + 'px';
      img.style.marginLeft = '3px';
      img.style.marginTop = '3px';
      img.style.marginRight = this.margin - 7 + 'px'; // -4 is the negative margin of the inline element
      img.style.marginBottom = this.margin - 7 + 'px';
    }
  };

  ImageLayout.prototype._alignImgs = function(imgGroup) {
    var slice, h,
    containerWidth = d.querySelector(this.container_selector).clientWidth;

    w: while (imgGroup.length > 0) {
      for (var i = 1; i <= imgGroup.length; i++) {
        slice = imgGroup.slice(0, i);
        h = this._getHeigth(slice, containerWidth);
        if (h < this.maxHeight) {
          this._setSize(slice, h);
          imgGroup = imgGroup.slice(i);
          continue w;
        }
      }
      this._setSize(slice, Math.min(this.maxHeight, h));
      break;
    }
  };

  ImageLayout.prototype.align = function(results_selector) {
    var results_selectorNode = d.querySelectorAll(this.results_selector),
    results_length = results_selectorNode.length,
    previous = null,
    current = null,
    imgGroup = [];
    for (var i = 0; i < results_length; i++) {
      current = results_selectorNode[i];
      if (current.previousElementSibling !== previous && imgGroup.length > 0) {
        // the current image is not conected to previous one
        // so the current image is the start of a new group of images.
        // so call _alignImgs to align the current group
        this._alignImgs(imgGroup);
        // and start a new empty group of images
        imgGroup = [];
      }
      // add the current image to the group (only the img tag)
      imgGroup.push(current.querySelector(this.img_selector));
      // update the previous variable
      previous = current;
    }
    // align the remaining images
    if (imgGroup.length > 0) {
      this._alignImgs(imgGroup);
    }
  };

  ImageLayout.prototype.watch = function() {
    var i, img, imgGroup, imgNodeLength,
    obj = this,
    results_nodes = d.querySelectorAll(this.results_selector),
    results_length = results_nodes.length;

    function align(e) {
      obj.align();
    }

    function throttleAlign(e) {
      if (obj._alignAllDone) {
        obj._alignAllDone = false;
        setTimeout(function() {
          obj.align();
          obj._alignAllDone = true;
        }, 100);
      }
    }

    w.addEventListener('resize', throttleAlign);
    w.addEventListener('pageshow', align);

    for (i = 0; i < results_length; i++) {
      img = results_nodes[i].querySelector(this.img_selector);
      if (typeof img !== 'undefined') {
        img.addEventListener('load', throttleAlign);
        img.addEventListener('error', throttleAlign);
      }
    }
  };

  w.searx.ImageLayout = ImageLayout;

})(window, document);
