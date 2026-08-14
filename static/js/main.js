/* ============================================================
   翼启神州 · 来华留学指南
   ============================================================ */

// ---------------------------------------------------------------------------
// 启动动画 - 苹果式满屏 logo
// ---------------------------------------------------------------------------
window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if (loader) {
    // 显示 1.2s 后淡出，防止闪烁
    setTimeout(() => {
      loader.classList.add('hide');
      setTimeout(() => loader.remove(), 600);
    }, 1200);
  }
});
// 兜底：无论什么情况，3 秒后强制隐藏 loader
setTimeout(() => {
  const loader = document.getElementById('loader');
  if (loader) {
    loader.classList.add('hide');
    setTimeout(() => loader.remove(), 600);
  }
}, 3000);

// ---------------------------------------------------------------------------
// 上下拉动式导航栏
// ---------------------------------------------------------------------------
(function initNavGrip() {
  const navbar = document.getElementById('navbar');
  const grip = document.getElementById('navGrip');
  if (!navbar || !grip) return;

  let collapsed = false;

  function toggle(force) {
    collapsed = (typeof force === 'boolean') ? force : !collapsed;
    navbar.classList.toggle('collapsed', collapsed);
    document.body.classList.toggle('nav-collapsed', collapsed);
    grip.title = collapsed ? '点击展开导航' : '点击收起导航';
  }

  grip.addEventListener('click', (e) => {
    e.stopPropagation();
    toggle();
  });

  // 导航栏始终跟随滚动，不自动收起（后台入口需一直可见）
  // 仅保留手动把手收起 / 双击回顶

  // 双击把手快速回到顶部
  grip.addEventListener('dblclick', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

// ---------------------------------------------------------------------------
// 通用：渐入观察器
// ---------------------------------------------------------------------------
(function initReveal() {
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
})();

// ---------------------------------------------------------------------------
// 中国地图交互
// ---------------------------------------------------------------------------
(function initChinaMap() {
  const map = document.getElementById('chinaMap');
  if (!map) return;

  // 学校数据（从 script 标签获取，由模板注入）
  const dataEl = document.getElementById('uniData');
  let unis = [];
  try {
    unis = JSON.parse(dataEl.textContent || '[]');
  } catch (e) { unis = []; }

  // 经纬度 → SVG 坐标（简化墨卡托投影，适配中国范围）
  // 经度 73~135 → x: 0~1000
  // 纬度 18~54 → y: 800~0（反向）
  function projectXY(lng, lat) {
    const x = ((lng - 73) / (135 - 73)) * 1000;
    const y = ((54 - lat) / (54 - 18)) * 800;
    return { x, y };
  }

  // 渲染所有标记 —— 方形印章样式（朱红方印 + 鎏金描边 + 学校名首字）
  const pinsLayer = document.getElementById('pinsLayer');
  function renderPins() {
    if (!pinsLayer) return;
    const lang = (window.getLang ? window.getLang() : (localStorage.getItem('lang') || 'zh'));
    const isEn = lang === 'en';
    pinsLayer.innerHTML = unis.map(u => {
      const { x, y } = projectXY(u.lng, u.lat);
      const label = isEn ? (u.name_en || u.name) : u.name;
      const firstChar = isEn ? ((label || 'U').charAt(0)) : ((u.name || '').charAt(0) || '学');
      return `
        <g class="map-pin" data-id="${u.id}" data-province="${u.province}" transform="translate(${x},${y})">
          <rect class="pin-pulse" x="-12" y="-12" width="24" height="24" rx="2"/>
          <rect class="pin-shadow" x="-10" y="-10" width="20" height="20" rx="2" transform="translate(1.5,1.5)"/>
          <rect class="pin-bg" x="-10" y="-10" width="20" height="20" rx="2"/>
          <rect class="pin-inner" x="-7" y="-7" width="14" height="14" rx="1"/>
          <text class="pin-char" x="0" y="4" text-anchor="middle">${firstChar}</text>
          <text class="pin-label" x="0" y="-16" text-anchor="middle">${label}</text>
        </g>
      `;
    }).join('');
  }
  renderPins();
  document.addEventListener('langchange', renderPins);

  // 点击省份方印 / 省份边界 → 跳转到城市页
  function goToCity(province) {
    if (!province) return;
    window.location.href = '/city/' + encodeURIComponent(province);
  }

  // 点击 pin：跳转到该省份城市页
  pinsLayer && pinsLayer.addEventListener('click', (e) => {
    const pin = e.target.closest('.map-pin');
    if (!pin) return;
    const province = pin.dataset.province;
    goToCity(province);
  });

  // 点击省份 path：跳转到城市页
  const provincePaths = map.querySelectorAll('path[data-province]');
  provincePaths.forEach(p => {
    p.addEventListener('click', () => {
      const prov = p.dataset.province;
      goToCity(prov);
    });
  });
})();

// ---------------------------------------------------------------------------
// 全部院校折叠浏览（地图页底部）
// 默认显示 8 所，点击展开全部，支持搜索与省份筛选
// ---------------------------------------------------------------------------
(function initAllUnisFold() {
  const grid = document.getElementById('allUnisGrid');
  if (!grid) return;
  const dataEl = document.getElementById('uniData');
  const unis = JSON.parse(dataEl.textContent || '[]');
  const toggleBtn = document.getElementById('allUnisToggle');
  const searchInput = document.getElementById('uniSearchInput');
  const provFilter = document.getElementById('uniProvinceFilter');
  const COLLAPSED_COUNT = 8;
  let expanded = false;

  // 填充省份下拉
  const provinces = [...new Set(unis.map(u => u.province))].sort();
  provinces.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p; opt.textContent = p;
    provFilter.appendChild(opt);
  });

  function filterList() {
    const kw = (searchInput.value || '').trim().toLowerCase();
    const prov = provFilter.value;
    return unis.filter(u => {
      if (prov && u.province !== prov) return false;
      if (kw) {
        const hay = (u.name + ' ' + (u.name_en || '') + ' ' + u.province).toLowerCase();
        if (!hay.includes(kw)) return false;
      }
      return true;
    });
  }

  function render() {
    const lang = window.getLang ? window.getLang() : (localStorage.getItem('lang') || 'zh');
    const list = filterList();
    const showCount = expanded ? list.length : Math.min(COLLAPSED_COUNT, list.length);
    const TAGS_EN = { '双一流': 'Double First-Class', '教育部直属': 'MOE Affiliated', 'C9联盟': 'C9 League', '九校联盟': 'C9 League' };
    grid.innerHTML = list.slice(0, showCount).map(u => {
      const name = lang === 'en' ? (u.name_en || u.name) : u.name;
      const prov = lang === 'en' ? (u.province_en || u.province) : u.province;
      const altName = lang === 'en' ? (u.name_en || u.name) : u.name;
      const tags = (u.tags || []).slice(0,2).map(t => lang === 'en' ? (TAGS_EN[t] || t) : t).join(' · ');
      return `
      <a class="all-uni-card" href="/university/${u.id}/">
        <div class="all-uni-seal"><img src="${u.badge}" alt="${altName}" loading="lazy"></div>
        <div class="all-uni-body">
          <div class="all-uni-name">${name}</div>
          <div class="all-uni-name-en">${lang === 'en' ? '' : (u.name_en || '')}</div>
          <div class="all-uni-meta">
            <span class="all-uni-prov">${prov}</span>
            <span class="all-uni-rank">${lang === 'en' ? 'Rank' : '排名'} ${u.ranking}</span>
            <span class="all-uni-tags">${tags}</span>
          </div>
        </div>
      </a>
    `;
    }).join('');
    if (!list.length) {
      grid.innerHTML = `<div style="grid-column:1/-1;padding:36px;text-align:center;color:var(--dai);font-family:var(--serif);">${lang === 'en' ? 'No results' : '无匹配院校'}</div>`;
    }
    // 更新按钮
    if (list.length <= COLLAPSED_COUNT) {
      toggleBtn.style.display = 'none';
    } else {
      toggleBtn.style.display = '';
      const zh = toggleBtn.querySelector('.lang-zh');
      const en = toggleBtn.querySelector('.lang-en');
      const arrow = toggleBtn.querySelector('.toggle-arrow');
      if (expanded) {
        zh.textContent = '收起';
        en.textContent = 'Show less';
        arrow.textContent = '▴';
      } else {
        zh.textContent = `展开全部 ${list.length} 所`;
        en.textContent = `Show all ${list.length}`;
        arrow.textContent = '▾';
      }
    }
  }

  // 监听语言切换
  document.addEventListener('langchange', (e) => {
    // 切换省份下拉为英文 / 中文
    const lang = (e.detail && e.detail.lang) || (window.getLang ? window.getLang() : (localStorage.getItem('lang') || 'zh'));
    provFilter.innerHTML = `<option value="">${lang === 'en' ? 'All provinces' : '全部省份'}</option>`;
    const provs = [...new Set(unis.map(u => lang === 'en' ? (u.province_en || u.province) : u.province))].sort();
    provs.forEach((p, i) => {
      const opt = document.createElement('option');
      opt.value = unis.find(u => (lang === 'en' ? (u.province_en || u.province) : u.province) === p).province;
      opt.textContent = p;
      provFilter.appendChild(opt);
    });
    // 同步搜索框 placeholder
    searchInput.placeholder = lang === 'en' ? 'Search by name...' : '搜索校名...';
    render();
  });

  toggleBtn.addEventListener('click', () => {
    expanded = !expanded;
    render();
    if (!expanded) {
      grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
  searchInput.addEventListener('input', () => { if (expanded) render(); else render(); });
  provFilter.addEventListener('change', () => { expanded = false; render(); });

  render();
})();

// ---------------------------------------------------------------------------
// 专业筛选
// ---------------------------------------------------------------------------
(function initProgramFilter() {
  const filterBox = document.getElementById('programFilter');
  if (!filterBox) return;

  const opts = filterBox.querySelectorAll('.filter-opt');
  const cards = document.querySelectorAll('.program-card');

  opts.forEach(opt => {
    opt.addEventListener('click', () => {
      const field = opt.dataset.field;
      const province = opt.dataset.province;
      opts.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');

      cards.forEach(card => {
        const cardField = card.dataset.field || '';
        const cardProvince = card.dataset.province || '';
        let show = true;
        if (field && cardField !== field) show = false;
        if (province && cardProvince !== province) show = false;
        card.style.display = show ? '' : 'none';
      });
    });
  });
})();

// ---------------------------------------------------------------------------
// 全站 UI 中英双语切换
// 切换 [data-zh]/[data-en] 元素文本；显示/隐藏 .lang-zh / .lang-en 容器
// ---------------------------------------------------------------------------
(function initLangSwitch() {
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
    // 0. 切换页面标题
    var metaTitle = document.querySelector('meta[name="title-' + lang + '"]');
    if (metaTitle) { document.title = metaTitle.getAttribute('content'); }
    // 1. 切换带 data-zh/data-en 的元素文本
    document.querySelectorAll('[data-zh][data-en]').forEach(el => {
      el.textContent = lang === 'zh' ? el.dataset.zh : el.dataset.en;
    });
    // 1b. 切换输入框 placeholder（data-placeholder-zh / data-placeholder-en）
    document.querySelectorAll('[data-placeholder-zh][data-placeholder-en]').forEach(el => {
      el.setAttribute('placeholder', lang === 'zh' ? el.getAttribute('data-placeholder-zh') : el.getAttribute('data-placeholder-en'));
    });
    // 1c. 切换图片 alt（data-alt-en 为英文；data-alt-zh 缺省时取原始 alt 作中文）
    document.querySelectorAll('img[data-alt-en]').forEach(el => {
      if (!el.hasAttribute('data-alt-zh')) el.setAttribute('data-alt-zh', el.getAttribute('alt') || '');
      el.setAttribute('alt', lang === 'en' ? el.getAttribute('data-alt-en') : el.getAttribute('data-alt-zh'));
    });
    // 1d. 翻译院校标签（中文标签 → 英文；已带 lang-zh/lang-en 子结构的跳过）
    var TAG_MAP = { '双一流': 'Double First-Class', '教育部直属': 'MOE Affiliated', 'C9联盟': 'C9 League', '九校联盟': 'C9 League' };
    document.querySelectorAll('.tag, .aside-tag').forEach(el => {
      if (el.querySelector('.lang-zh, .lang-en')) return;
      if (!el.hasAttribute('data-tag-zh')) el.setAttribute('data-tag-zh', el.textContent.trim());
      var zh = el.getAttribute('data-tag-zh');
      el.textContent = (lang === 'en' && TAG_MAP[zh]) ? TAG_MAP[zh] : zh;
    });
    // 2. 显示/隐藏 .lang-zh / .lang-en 双语容器
    document.querySelectorAll('.lang-zh').forEach(el => {
      setLangDisplay(el, lang === 'zh');
    });
    document.querySelectorAll('.lang-en').forEach(el => {
      setLangDisplay(el, lang === 'en');
    });
    // 3. body 标记当前语言，便于 CSS 定制
    document.body.classList.toggle('lang-en-active', lang === 'en');
    // 4. 派发事件，供其他模块（如地图、院校列表）使用
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
  }

  // 暴露全局方法（必须在 applyLang 之前定义，确保 langchange 处理器能使用）
  window.getLang = () => localStorage.getItem('lang') || 'zh';
  window.setLang = (lang) => {
    localStorage.setItem('lang', lang);
    buttons.forEach(b => b.classList.toggle('active', b.dataset.lang === lang));
    applyLang(lang);
  };

  // 设置初始状态
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
})();
