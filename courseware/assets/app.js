/* 星辰智脑 (StarMind) 70天实战课件交互脚本 */
(function () {
  // 1. 主题切换与本地记忆
  const savedTheme = localStorage.getItem("starmind_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);

  window.setTheme = function (theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("starmind_theme", theme);
  };

  // 2. 顶部阅读进度条与目录高亮
  const progressEl = document.getElementById("read-progress");
  const tocLinks = Array.from(document.querySelectorAll(".toc-list a"));
  const sections = tocLinks
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  function updateScroll() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (progressEl && docHeight > 0) {
      progressEl.style.width = Math.min(100, (scrollTop / docHeight) * 100) + "%";
    }
    let currentId = "";
    for (const sec of sections) {
      if (sec.getBoundingClientRect().top <= 120) {
        currentId = sec.id;
      }
    }
    tocLinks.forEach((a) => {
      a.classList.toggle("active", a.getAttribute("href") === "#" + currentId);
    });
  }
  window.addEventListener("scroll", updateScroll, { passive: true });
  updateScroll();

  // 3. 代码一键复制
  window.copyCode = function (btn) {
    const pre = btn.closest(".code-block-wrap").querySelector("pre");
    if (!pre) return;
    navigator.clipboard.writeText(pre.innerText).then(() => {
      const oldText = btn.innerText;
      btn.innerText = "已复制 ✓";
      setTimeout(() => (btn.innerText = oldText), 1800);
    });
  };

  // 4. 课后作业参考答案展开/收起
  window.toggleSolution = function (btn, id) {
    const el = document.getElementById(id);
    if (!el) return;
    const isOpen = el.classList.toggle("open");
    btn.innerText = isOpen ? "收起参考答案" : "查看标准答案与解析";
  };

  // 5. 标记今日已学完（存入 localStorage 供总门户进度条读取）
  window.toggleDayComplete = function (dayNum, btn) {
    const key = "starmind_completed_days";
    let list = [];
    try { list = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) {}
    const idx = list.indexOf(dayNum);
    if (idx >= 0) {
      list.splice(idx, 1);
      btn.innerText = "标记今日已完成";
      btn.classList.remove("btn-primary");
    } else {
      list.push(dayNum);
      btn.innerText = "今日已打卡 ✓";
      btn.classList.add("btn-primary");
    }
    localStorage.setItem(key, JSON.stringify(list));
  };

  // 初始化打卡按钮状态
  const completeBtn = document.getElementById("complete-day-btn");
  if (completeBtn) {
    const dayNum = parseInt(completeBtn.dataset.day, 10);
    try {
      const list = JSON.parse(localStorage.getItem("starmind_completed_days") || "[]");
      if (list.includes(dayNum)) {
        completeBtn.innerText = "今日已打卡 ✓";
        completeBtn.classList.add("btn-primary");
      }
    } catch (e) {}
  }
})();
