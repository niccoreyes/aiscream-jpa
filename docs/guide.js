document.getElementById('print-guide').addEventListener('click', () => window.print());
const sections = [document.getElementById('overview'), ...document.querySelectorAll('main section')];
const links = document.querySelectorAll('aside nav a');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      for (const link of links) {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }
    }
  }, { rootMargin: '-5% 0px -65% 0px' });
  sections.forEach(section => observer.observe(section));
}
document.querySelectorAll('.mobile-nav a').forEach(link => {
  link.addEventListener('click', () => { document.querySelector('.mobile-nav').open = false; });
});
