// 图片滑动器功能
let currentImageSlide = 0;

function slideImages(direction) {
    const slider = document.getElementById('image-slider');
    const slides = slider.querySelectorAll('.slide');
    const slideWidth = slides[0].offsetWidth + 20; // 包含gap
    
    currentImageSlide += direction;
    
    // 边界检查
    if (currentImageSlide < 0) {
        currentImageSlide = 0;
    }
    
    const maxSlide = slides.length - Math.floor(slider.parentElement.offsetWidth / slideWidth);
    if (currentImageSlide > maxSlide) {
        currentImageSlide = maxSlide;
    }
    
    slider.scrollTo({
        left: currentImageSlide * slideWidth,
        behavior: 'smooth'
    });
}

// 平滑滚动到锚点
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// 导航栏滚动效果
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.nav');
    if (window.scrollY > 50) {
        nav.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
    } else {
        nav.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
    }
});

// 简单的懒加载（当实际图片加入时使用）
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        }
    });
}, observerOptions);

// 观察所有带有 data-src 属性的图片
document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
});

console.log('🎨 泡泡的AI作品集网站已加载完成');
console.log('📸 等待 Week 1 生图作品上传...');
console.log('🎬 等待 Week 2 视频作品上传...');
console.log('⚙️ 等待 Week 3 工作流作品上传...');
