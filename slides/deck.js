/* ================================================
   BUILD CAT MASCOT HTML
================================================ */
function buildCat(opts = {}) {
    const { expression = 'happy', speed = '1.7s', tag = 'Nyom 😼' } = opts;

    const eyeHappy  = `<div class="meye L"><span class="mpupil"></span><span class="mblink"></span></div><div class="meye R"><span class="mpupil"></span><span class="mblink"></span></div>`;
    const eyeWorried= `<div class="meye L" style="background:#fff;"><span style="position:absolute;width:10px;height:6px;border-top:3px solid #1A1A1A;border-radius:50% 50% 0 0;top:7px;left:5px;"></span></div><div class="meye R" style="background:#fff;"><span style="position:absolute;width:10px;height:6px;border-top:3px solid #1A1A1A;border-radius:50% 50% 0 0;top:7px;left:5px;"></span></div>`;
    const eyeStar   = `<div class="meye L" style="display:flex;align-items:center;justify-content:center;font-size:14px;">⭐</div><div class="meye R" style="display:flex;align-items:center;justify-content:center;font-size:14px;">⭐</div>`;
    const eyeHeart  = `<div class="meye L" style="display:flex;align-items:center;justify-content:center;font-size:12px;">🩷</div><div class="meye R" style="display:flex;align-items:center;justify-content:center;font-size:12px;">🩷</div>`;

    const mouthHappy  = `<div class="mmouth"></div>`;
    const mouthWorried= `<div style="position:absolute;width:36px;height:17px;border:4px solid #fff;border-radius:18px 18px 0 0;border-bottom:none;bottom:24px;left:50%;transform:translateX(-50%);"></div>`;
    const mouthLaugh  = `<div style="position:absolute;width:44px;height:22px;border:4px solid #fff;border-radius:0 0 22px 22px;border-top:none;bottom:22px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.15);overflow:hidden;"></div>`;

    const eyes  = expression==='worried'?eyeWorried : expression==='star'?eyeStar : expression==='heart'?eyeHeart : eyeHappy;
    const mouth = expression==='worried'?mouthWorried : expression==='laugh'?mouthLaugh : mouthHappy;

    const extras = expression==='worried' ? `<div style="position:absolute;top:8px;right:5px;width:9px;height:13px;background:rgba(91,158,166,.7);border-radius:50% 50% 60% 60%;transform:rotate(15deg);animation:blobDrift 2.8s ease-in-out infinite;"></div>` : '';

    return `
        <div class="mascot-bounce" style="animation-duration:${speed}">
            <div class="mbody">
                <div class="mear L"></div><div class="mear R"></div>
                <div class="mwhisk l1"></div><div class="mwhisk l2"></div><div class="mwhisk l3"></div>
                <div class="mwhisk r1"></div><div class="mwhisk r2"></div><div class="mwhisk r3"></div>
                <div class="mnose"></div>
                <div class="marm L"></div>
                <div class="marm R"><div class="mcoin">¢</div></div>
                ${eyes}
                <div class="mcheek L"></div><div class="mcheek R"></div>
                ${mouth}
                ${extras}
                <div class="mtail"></div>
                <div class="mleg L"></div><div class="mleg R"></div>
            </div>
        </div>
        <div class="mshadow"></div>`;
}

const cats = {
    's1':  { expression:'happy',   speed:'1.5s', tag:'Nyom 😼' },
    's2':  { expression:'heart',   speed:'1.7s', tag:'Nyom 😼' },
    's3':  { expression:'worried', speed:'2.2s', tag:'uh oh 😿' },
    's4':  { expression:'star',    speed:'1.1s', tag:'slay 😼✨' },
    's5':  { expression:'happy',   speed:'1.6s', tag:'Nyom 😼' },
    's6':  { expression:'happy',   speed:'1.8s', tag:'Nyom 😼' },
    's7':  { expression:'laugh',   speed:'0.9s', tag:'LFG 😹🔥' },
    's8':  { expression:'heart',   speed:'1.5s', tag:'bye!! 🐾' },
};

Object.entries(cats).forEach(([id, opts]) => {
    const el = document.getElementById('cat-' + id);
    if (el) el.innerHTML = buildCat(opts);
});

/* ================================================
   PER-SLIDE THEMED PARTICLES
================================================ */
const slideThemes = {
    's1': { coins:6, sparks:6, items:['💰','✦','🌟','💎','✨','🎉','🪙'],    paws:2 },
    's2': { coins:0, sparks:3, items:['🐾','💙','🐱','🤝','💪','✨'],         paws:6 },
    's3': { coins:0, sparks:3, items:['💸','😿','💔','📉','❌','😰'],          paws:0, badCoins:4 },
    's4': { coins:5, sparks:7, items:['✨','🏠','🌟','🔓','⭐','🎊','🗝️'],   paws:2 },
    's5': { coins:0, sparks:9, items:['⚡','💻','⚙️','🐍','⚛️','🗄️','🔧'],  paws:0 },
    's6': { coins:3, sparks:4, items:['🪑','🛏️','📊','🏺','⬆️','🪟','🪴'],  paws:1 },
    's7': { coins:4, sparks:5, items:['🎮','🔥','⚡','🏆','🎯','🕹️','💥'],   paws:2 },
    's8': { coins:2, sparks:4, items:['💬','❓','🐾','💭','🙋','💕','🫶'],    paws:4 },
};

function edgePos() {
    const zone = Math.floor(Math.random() * 4);
    if (zone === 0) return { l: `${2+Math.random()*96}%`,   t: `${2+Math.random()*12}%` };
    if (zone === 1) return { l: `${2+Math.random()*96}%`,   b: `${2+Math.random()*12}%` };
    if (zone === 2) return { l: `${Math.random()*14}%`,      t: `${14+Math.random()*72}%` };
    return                 { l: `${86+Math.random()*14}%`,   t: `${14+Math.random()*72}%` };
}

function posCss(p) {
    let s = `left:${p.l};`;
    if (p.t) s += `top:${p.t};`;
    if (p.b) s += `bottom:${p.b};`;
    return s;
}

function addParticles(slide, id) {
    const cfg  = slideThemes[id] || { coins:4, sparks:5, items:['✦','✸','★'], paws:1 };
    const clrs = ['var(--teal)','var(--coral)','var(--gold)'];

    for (let i = 0; i < cfg.coins; i++) {
        const e = document.createElement('div');
        e.className = 'coin-p';
        e.textContent = '¢';
        const p = edgePos();
        e.style.cssText = posCss(p) + `animation-delay:${Math.random()*5}s;animation-duration:${3.5+Math.random()*4}s;`;
        slide.prepend(e);
    }

    for (let i = 0; i < (cfg.badCoins||0); i++) {
        const e = document.createElement('div');
        e.className = 'coin-p';
        e.textContent = '¢';
        e.style.background = 'var(--coral)';
        e.style.borderColor = '#8B1A0A';
        e.style.color = '#fff';
        const p = edgePos();
        e.style.cssText += posCss(p) + `animation-delay:${Math.random()*5}s;animation-duration:${4+Math.random()*3}s;background:var(--coral);border-color:#8B1A0A;color:#fff;`;
        slide.prepend(e);
    }

    for (let i = 0; i < cfg.sparks; i++) {
        const e = document.createElement('div');
        e.className = 'spark-p ' + ['t','c','g'][Math.floor(Math.random()*3)];
        const p = edgePos();
        e.style.cssText = posCss(p) + `animation-delay:${Math.random()*6}s;animation-duration:${1.8+Math.random()*3}s;`;
        slide.prepend(e);
    }

    for (let i = 0; i < cfg.items.length; i++) {
        const e = document.createElement('div');
        e.className = 'star-p';
        e.textContent = cfg.items[i % cfg.items.length];
        const p = edgePos();
        const sz = 14 + Math.floor(Math.random() * 10);
        e.style.cssText = posCss(p) + `color:${clrs[Math.floor(Math.random()*clrs.length)]};font-size:${sz}px;animation-delay:${Math.random()*5}s;animation-duration:${3+Math.random()*3}s;`;
        slide.prepend(e);
    }

    for (let i = 0; i < cfg.paws; i++) {
        const e = document.createElement('div');
        e.className = 'paw-p';
        e.textContent = '🐾';
        const p = edgePos();
        e.style.cssText = posCss(p) + `animation-delay:${Math.random()*6}s;animation-duration:${4+Math.random()*3}s;opacity:0;`;
        slide.prepend(e);
    }
}

document.querySelectorAll('.slide').forEach(s => addParticles(s, s.id));

/* ================================================
   PRESENTATION CONTROLLER
================================================ */
class Deck {
    constructor() {
        this.slides = Array.from(document.querySelectorAll('.slide'));
        this.stage  = document.getElementById('deckStage');
        this.cur    = 0;
        this.scaleStage();
        window.addEventListener('resize', () => this.scaleStage());
        this.bindKeys(); this.bindTouch(); this.bindWheel();
        this.go(0);
    }
    scaleStage() {
        const f = Math.min(window.innerWidth/1920, window.innerHeight/1080);
        const x = (window.innerWidth  - 1920*f)/2;
        const y = (window.innerHeight - 1080*f)/2;
        this.stage.style.transform = `translate(${x}px,${y}px) scale(${f})`;
    }
    go(idx) {
        this.cur = Math.max(0, Math.min(idx, this.slides.length-1));
        this.slides.forEach((s, i) => {
            const on = i === this.cur;
            s.classList.toggle('active', on);
            if (on) { requestAnimationFrame(() => requestAnimationFrame(() => s.classList.add('visible'))); }
            else      { s.classList.remove('visible'); }
        });
    }
    next() { this.go(this.cur+1); }
    prev() { this.go(this.cur-1); }
    bindKeys() {
        document.addEventListener('keydown', e => {
            if (e.target.getAttribute('contenteditable')) return;
            if ([' ','ArrowRight','ArrowDown','PageDown'].includes(e.key)) { e.preventDefault(); this.next(); }
            if (['ArrowLeft','ArrowUp','PageUp'].includes(e.key))           { e.preventDefault(); this.prev(); }
            if (e.key==='Home') this.go(0);
            if (e.key==='End')  this.go(this.slides.length-1);
        });
    }
    bindTouch() {
        let sx=0, sy=0;
        this.stage.addEventListener('touchstart', e => { sx=e.touches[0].clientX; sy=e.touches[0].clientY; }, {passive:true});
        this.stage.addEventListener('touchend',   e => {
            const dx=e.changedTouches[0].clientX-sx, dy=e.changedTouches[0].clientY-sy;
            if (Math.abs(dx)>Math.abs(dy) && Math.abs(dx)>48) dx<0?this.next():this.prev();
        }, {passive:true});
    }
    bindWheel() {
        let last=0;
        document.addEventListener('wheel', e => {
            const now=Date.now(); if (now-last<600) return; last=now;
            e.deltaY>0?this.next():this.prev();
        }, {passive:true});
    }
}

/* ================================================
   INLINE EDITOR
================================================ */
class Editor {
    constructor() { this.on=false; this.els=[]; }
    toggle() {
        this.on = !this.on;
        const btn = document.getElementById('editToggle');
        if (this.on) {
            btn.textContent='💾'; btn.classList.add('active');
            document.querySelectorAll('.slide *').forEach(el => {
                if (!el.children.length && el.textContent.trim() && !el.closest('.mascot-scene') && !el.closest('.coin-p') && !el.closest('.spark-p')) {
                    el.contentEditable='true'; this.els.push(el);
                }
            });
        } else {
            btn.textContent='✏️'; btn.classList.remove('active');
            this.els.forEach(el => el.removeAttribute('contenteditable')); this.els=[];
        }
    }
}

const deck   = new Deck();
const editor = new Editor();

const hotzone = document.getElementById('editHotzone');
const editBtn = document.getElementById('editToggle');
let hideTimer = null;
const showBtn = () => { clearTimeout(hideTimer); editBtn.classList.add('show'); };
const hideBtn = () => { hideTimer = setTimeout(()=>{ if(!editor.on) editBtn.classList.remove('show'); }, 400); };
hotzone.addEventListener('mouseenter', showBtn); hotzone.addEventListener('mouseleave', hideBtn);
editBtn.addEventListener('mouseenter', showBtn); editBtn.addEventListener('mouseleave', hideBtn);
hotzone.addEventListener('click', ()=>editor.toggle());
editBtn.addEventListener('click',  ()=>editor.toggle());
document.addEventListener('keydown', e => {
    if ((e.key==='e'||e.key==='E') && !e.target.getAttribute('contenteditable')) editor.toggle();
});
