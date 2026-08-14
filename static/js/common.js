/* ============================================================
   翼启神州 · 来华留学指南 - 纯前端共享库
   ============================================================ */

// ---------------------------------------------------------------------------
// 全局数据缓存
// ---------------------------------------------------------------------------
window.APP_DATA = {
  universities: [],
  loaded: false,
  loadPromise: null
};

// 数据加载
window.APP_DATA.loadPromise = fetch('data/universities.json')
  .then(r => r.json())
  .then(data => {
    window.APP_DATA.universities = data;
    window.APP_DATA.loaded = true;
    return data;
  })
  .catch(err => {
    console.error('Failed to load universities data:', err);
    return [];
  });

// 工具函数
window.AppUtils = {
  // 获取所有省份
  allProvinces: function() {
    const provinces = new Map();
    window.APP_DATA.universities.forEach(u => {
      if (u.province && !provinces.has(u.province)) {
        provinces.set(u.province, u.province_en || u.province);
      }
    });
    return Array.from(provinces.entries()).map(([zh, en]) => ({ zh, en }));
  },

  // 获取所有专业
  allFields: function() {
    const fields = new Map();
    window.APP_DATA.universities.forEach(u => {
      (u.programs || []).forEach((p, i) => {
        if (!fields.has(p)) {
          fields.set(p, (u.programs_en && u.programs_en[i]) ? u.programs_en[i] : p);
        }
      });
    });
    return Array.from(fields.entries()).map(([zh, en]) => ({ zh, en }));
  },

  // 层级名称映射
  tierNames: { "C9": "C9联盟", "985": "985工程", "211": "211工程", "双一流": "双一流", "普通": "综合大学", "学院": "专业学院" },
  tierNamesEn: { "C9": "C9 League", "985": "Project 985", "211": "Project 211", "双一流": "Double First-Class", "普通": "Comprehensive", "学院": "Academy" },

  // 标签翻译
  TAG_MAP: { '双一流': 'Double First-Class', '教育部直属': 'MOE Affiliated', 'C9联盟': 'C9 League', '九校联盟': 'C9 League' },

  // 获取 URL 参数
  getParam: function(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
  },

  // 年份
  year: new Date().getFullYear()
};

// ---------------------------------------------------------------------------
// 启动动画
// ---------------------------------------------------------------------------
(function initLoader() {
  window.addEventListener('load', () => {
    const loader = document.getElementById('loader');
    if (loader) {
      setTimeout(() => {
        loader.classList.add('hide');
        setTimeout(() => loader.remove(), 600);
      }, 1200);
    }
  });
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) {
      loader.classList.add('hide');
      setTimeout(() => loader.remove(), 600);
    }
  }, 3000);
})();

// ---------------------------------------------------------------------------
// 渐入观察器
// ---------------------------------------------------------------------------
(function initReveal() {
  document.addEventListener('DOMContentLoaded', () => {
    const reveals = document.querySelectorAll('[data-reveal]');
    if (!reveals.length || !('IntersectionObserver' in window)) {
      reveals.forEach(el => el.classList.add('revealed'));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    reveals.forEach(el => io.observe(el));
  });
})();

// ---------------------------------------------------------------------------
// 语言切换
// ---------------------------------------------------------------------------
(function initLangSwitch() {
  document.addEventListener('DOMContentLoaded', () => {
    const switchEl = document.getElementById('langSwitch');
    if (!switchEl) return;
    const buttons = switchEl.querySelectorAll('button');
    let currentLang = localStorage.getItem('lang') || 'zh';

    function setLangDisplay(el, show) {
      if (!show) { el.style.display = 'none'; return; }
      const tag = el.tagName.toLowerCase();
      if (tag === 'span' || tag === 'a' || tag === 'button' || tag === 'label' || tag === 'text' || tag === 'option') {
        el.style.display = 'inline';
      } else if (tag === 'p' || tag === 'div' || tag === 'h1' || tag === 'h2' || tag === 'h3' || tag === 'h4' || tag === 'li') {
        el.style.display = 'block';
      } else {
        el.style.display = 'revert';
      }
    }

    function applyLang(lang) {
      document.documentElement.setAttribute('lang', lang === 'zh' ? 'zh-CN' : 'en');
      // 页面标题
      const metaTitle = document.querySelector('meta[name="title-' + lang + '"]');
      if (metaTitle) { document.title = metaTitle.getAttribute('content'); }
      // data-zh/data-en 文本
      document.querySelectorAll('[data-zh][data-en]').forEach(el => {
        el.textContent = lang === 'zh' ? el.dataset.zh : el.dataset.en;
      });
      // placeholder
      document.querySelectorAll('[data-placeholder-zh][data-placeholder-en]').forEach(el => {
        el.setAttribute('placeholder', lang === 'zh' ? el.getAttribute('data-placeholder-zh') : el.getAttribute('data-placeholder-en'));
      });
      // img alt
      document.querySelectorAll('img[data-alt-en]').forEach(el => {
        if (!el.hasAttribute('data-alt-zh')) el.setAttribute('data-alt-zh', el.getAttribute('alt') || '');
        el.setAttribute('alt', lang === 'en' ? el.getAttribute('data-alt-en') : el.getAttribute('data-alt-zh'));
      });
      // 标签翻译
      var TAG_MAP = window.AppUtils.TAG_MAP;
      document.querySelectorAll('.tag, .aside-tag').forEach(el => {
        if (el.querySelector('.lang-zh, .lang-en')) return;
        if (!el.hasAttribute('data-tag-zh')) el.setAttribute('data-tag-zh', el.textContent.trim());
        var zh = el.getAttribute('data-tag-zh');
        el.textContent = (lang === 'en' && TAG_MAP[zh]) ? TAG_MAP[zh] : zh;
      });
      // lang-zh / lang-en
      document.querySelectorAll('.lang-zh').forEach(el => { setLangDisplay(el, lang === 'zh'); });
      document.querySelectorAll('.lang-en').forEach(el => { setLangDisplay(el, lang === 'en'); });
      // body
      document.body.classList.toggle('lang-en-active', lang === 'en');
      // 事件
      document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
    }

    window.getLang = () => localStorage.getItem('lang') || 'zh';
    window.setLang = (lang) => {
      localStorage.setItem('lang', lang);
      buttons.forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
      applyLang(lang);
    };

    buttons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === currentLang);
    });
    applyLang(currentLang);

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const lang = btn.dataset.lang;
        if (lang === currentLang) return;
        currentLang = lang;
        localStorage.setItem('lang', lang);
        buttons.forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
        applyLang(lang);
      });
    });
  });
})();

// ---------------------------------------------------------------------------
// 图片懒加载 + 加载动画
// ---------------------------------------------------------------------------
(function initImageLoading() {
  document.addEventListener('DOMContentLoaded', function() {
    // 为所有图片添加加载动画
    var imgs = document.querySelectorAll('img:not(.loader-logo)');
    imgs.forEach(function(img) {
      // 跳过已加载的
      if (img.complete && img.naturalWidth > 0) {
        img.classList.add('loaded');
        return;
      }
      img.classList.add('img-load');
      img.addEventListener('load', function() {
        img.classList.add('loaded');
      });
      img.addEventListener('error', function() {
        img.classList.add('loaded');
      });
      // 兜底：3秒后强制显示
      setTimeout(function() {
        img.classList.add('loaded');
      }, 3000);
    });

    // 为图片容器添加骨架屏
    var containers = document.querySelectorAll('.uni-card-img, .gallery-main, .gallery-cell, .uni-badge-img, .uni-detail-seal');
    containers.forEach(function(c) {
      if (!c.querySelector('img')) return;
      c.classList.add('img-skeleton');
      var img = c.querySelector('img');
      if (img.complete && img.naturalWidth > 0) {
        c.classList.remove('img-skeleton');
      }
      img.addEventListener('load', function() {
        c.classList.remove('img-skeleton');
      });
      img.addEventListener('error', function() {
        c.classList.remove('img-skeleton');
      });
    });
  });
})();

// ---------------------------------------------------------------------------
// Lightbox 图片预览
// ---------------------------------------------------------------------------
(function initLightbox() {
  var lightbox = null;
  var galleryImages = [];
  var currentIdx = 0;

  function createLightbox() {
    if (lightbox) return;
    lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML =
      '<button class="lightbox-close">&times;</button>' +
      '<button class="lightbox-nav lightbox-prev">&lsaquo;</button>' +
      '<button class="lightbox-nav lightbox-next">&rsaquo;</button>' +
      '<img src="" alt="">' +
      '<div class="lightbox-counter"></div>';
    document.body.appendChild(lightbox);

    var closeBtn = lightbox.querySelector('.lightbox-close');
    var prevBtn = lightbox.querySelector('.lightbox-prev');
    var nextBtn = lightbox.querySelector('.lightbox-next');
    var img = lightbox.querySelector('img');

    function close() {
      lightbox.classList.remove('show');
      document.body.style.overflow = '';
    }

    function show(idx) {
      if (idx < 0 || idx >= galleryImages.length) return;
      currentIdx = idx;
      img.src = galleryImages[currentIdx];
      lightbox.querySelector('.lightbox-counter').textContent =
        (currentIdx + 1) + ' / ' + galleryImages.length;
      lightbox.classList.add('show');
      document.body.style.overflow = 'hidden';
      prevBtn.style.display = galleryImages.length > 1 ? '' : 'none';
      nextBtn.style.display = galleryImages.length > 1 ? '' : 'none';
    }

    closeBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      close();
    });

    lightbox.addEventListener('click', function(e) {
      if (e.target === lightbox) close();
    });

    prevBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      show(currentIdx - 1);
    });

    nextBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      show(currentIdx + 1);
    });

    document.addEventListener('keydown', function(e) {
      if (!lightbox.classList.contains('show')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(currentIdx - 1);
      if (e.key === 'ArrowRight') show(currentIdx + 1);
    });

    // 暴露给页面
    window.openLightbox = function(images, idx) {
      galleryImages = Array.isArray(images) ? images : [images];
      show(idx || 0);
    };
  }

  document.addEventListener('DOMContentLoaded', function() {
    createLightbox();

    // 画廊图片点击
    document.addEventListener('click', function(e) {
      var cell = e.target.closest('.gallery-cell, .gallery-main');
      if (!cell) return;
      var allCells = cell.closest('.campus-gallery');
      if (!allCells) {
        var img = cell.querySelector('img');
        if (img) window.openLightbox([img.src], 0);
        return;
      }
      var imgs = Array.from(allCells.querySelectorAll('.gallery-cell img, .gallery-main img'))
        .map(function(i) { return i.src; });
      var clickedImg = cell.querySelector('img');
      var idx = imgs.indexOf(clickedImg ? clickedImg.src : imgs[0]);
      window.openLightbox(imgs, idx >= 0 ? idx : 0);
    });
  });
})();