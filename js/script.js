'use strict';

document.addEventListener('DOMContentLoaded', () => {
  const viewButtons = document.querySelectorAll('.sprint-switch__button[data-view]');
  const viewContent = document.querySelectorAll('[data-view-content]');

  const setView = (view) => {
    const activeView = view === 'society' ? 'society' : 'sprint';

    viewContent.forEach((content) => {
      content.hidden = content.dataset.viewContent !== activeView;
    });

    viewButtons.forEach((button) => {
      const isActive = button.dataset.view === activeView;
      button.classList.toggle('is-active', isActive);
      button.setAttribute('aria-current', isActive ? 'page' : 'false');
    });
  };

  const viewFromHash = () => window.location.hash === '#society-5' ? 'society' : 'sprint';
  setView(viewFromHash());
  window.addEventListener('hashchange', () => setView(viewFromHash()));

  const triggers = document.querySelectorAll('.image-trigger');

  if (!triggers.length) {
    return;
  }

  const lightbox = document.createElement('dialog');
  lightbox.className = 'image-lightbox';
  lightbox.innerHTML = `
    <div class="image-lightbox__content">
      <button class="image-lightbox__close" type="button" aria-label="Sluit vergrote afbeelding">&times;</button>
      <img class="image-lightbox__image" alt="">
    </div>
  `;
  document.body.append(lightbox);

  const image = lightbox.querySelector('.image-lightbox__image');
  const closeButton = lightbox.querySelector('.image-lightbox__close');

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      image.src = trigger.dataset.image;
      image.alt = trigger.dataset.alt;
      image.classList.remove('is-zoomed');
      lightbox.showModal();
      closeButton.focus();
    });
  });

  image.addEventListener('click', () => {
    image.classList.toggle('is-zoomed');
  });

  closeButton.addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) {
      lightbox.close();
    }
  });
  lightbox.addEventListener('close', () => {
    image.removeAttribute('src');
    image.alt = '';
    image.classList.remove('is-zoomed');
  });
});
