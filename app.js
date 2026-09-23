(() => {
  'use strict';
  // A file:// folder does not resolve index.html like a web server does.
  // Keep clean, crawlable URLs on HTTP(S); adapt only the offline preview.
  if (location.protocol === 'file:') {
    const siteRoot = new URL('./', document.currentScript.src);
    const adaptLink = link => {
      const raw = link.getAttribute('href');
      if (!raw || raw.startsWith('#')) return;
      let target;
      try {
        target = raw.startsWith('/') && !raw.startsWith('//') ? new URL(raw.slice(1), siteRoot) : new URL(raw, location.href);
      } catch { return; }
      if (target.protocol !== 'file:' || !target.pathname.startsWith(siteRoot.pathname)) return;
      if (target.pathname.endsWith('/')) target.pathname += 'index.html';
      link.setAttribute('href', target.href);
    };
    const adaptTree = root => {
      if (root.nodeType !== Node.ELEMENT_NODE) return;
      if (root.matches('a[href]')) adaptLink(root);
      root.querySelectorAll('a[href]').forEach(adaptLink);
    };
    adaptTree(document.body);
    // The homepage replaces product cards when a category/sort is selected.
    new MutationObserver(records => {
      for (const record of records) record.addedNodes.forEach(adaptTree);
    }).observe(document.body, {childList:true, subtree:true});
  }
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const products = window.PATTAYA_PRODUCTS || [];
  const money = n => new Intl.NumberFormat('ru-RU', { maximumFractionDigits:0 }).format(n) + ' ₽';
  const paths = {arrow:'M4 12h16m-6-6 6 6-6 6',diagonal:'M5 19 19 5M5 5h14v14'};
  const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const icon = name => `<svg class="icon icon-${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="${paths[name]}"/></svg>`;
  $('#year').textContent = new Date().getFullYear();

  const menu = $('.menu-toggle');
  function closeMenu() { menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','Открыть меню'); $('#navigation').classList.remove('open'); }
  menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded',String(open)); menu.setAttribute('aria-label',open?'Закрыть меню':'Открыть меню'); $('#navigation').classList.toggle('open',open); });
  $$('#navigation a').forEach(a => a.addEventListener('click',closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); } });
  matchMedia('(min-width:761px)').addEventListener('change',closeMenu);

  function keyboardTabs(tabs, activate) {
    tabs.forEach((button,index) => button.addEventListener('keydown', e => {
      let next;
      if (e.key === 'ArrowRight') next=(index+1)%tabs.length;
      if (e.key === 'ArrowLeft') next=(index+tabs.length-1)%tabs.length;
      if (e.key === 'Home') next=0;
      if (e.key === 'End') next=tabs.length-1;
      if (next !== undefined) { e.preventDefault(); activate(tabs[next]); tabs[next].focus(); }
    }));
  }
  function markTabs(tabs,selected) { tabs.forEach(button => { const on=button===selected; button.setAttribute('aria-selected',String(on)); button.tabIndex=on?0:-1; }); }
  let category='massage';
  const categoryTabs=$$('button[data-category]');
  function renderProducts() {
    const filtered=products.filter(p=>p.category===category);
    const sort=$('#catalog-sort').value;
    if(sort!=='default') filtered.sort((a,b)=>sort==='asc'?a.price-b.price:b.price-a.price);
    $('#product-grid').dataset.category=category;
    $('#product-grid').innerHTML=filtered.map(p=>`<article class="product-card"><a class="product-photo" href="${escape(p.url)}" aria-label="${escape(p.title)}: состав и цена"><img src="assets/${escape(p.image)}.webp" alt="${escape(p.title)} — фото из материалов салона Паттайя" width="520" height="570" loading="lazy"><span class="product-time">${escape(p.time)}</span><span class="photo-arrow">${icon('diagonal')}</span></a><div class="product-card-copy"><h3><a href="${escape(p.url)}">${escape(p.title)}</a></h3><p>${escape(p.caption)}</p><div><span>${p.from?'от ':''}${money(p.price)}${p.category==='couple'?' <small>/ двоих</small>':''}</span><a class="product-link" href="${escape(p.url)}" aria-label="Состав программы ${escape(p.title)}">Подробнее ${icon('arrow')}</a></div></div></article>`).join('');
  }
  function selectCategory(button) { category=button.dataset.category; markTabs(categoryTabs,button); $('#product-grid').setAttribute('aria-labelledby',button.id); renderProducts(); }
  categoryTabs.forEach(button=>button.addEventListener('click',()=>selectCategory(button)));
  keyboardTabs(categoryTabs,selectCategory);
  $('#catalog-sort')?.addEventListener('change',renderProducts);

  const occasionTabs=$$('[data-occasion]');
  function selectOccasion(button) { markTabs(occasionTabs,button); const friends=button.dataset.occasion==='friends'; $('#couple-content').hidden=friends; $('#friends-content').hidden=!friends; $('#occasion-panel').setAttribute('aria-labelledby',button.id); }
  occasionTabs.forEach(button=>button.addEventListener('click',()=>selectOccasion(button)));
  keyboardTabs(occasionTabs,selectOccasion);
  const groupPrices={2:4600,3:4500,4:4400,5:4300,6:4200};
  function groupSelection() { const guests=Number($('#guest-count').value); return {guests,each:groupPrices[guests],total:guests*groupPrices[guests]}; }
  $('#guest-count')?.addEventListener('change',()=>{const group=groupSelection(); $('#guest-price').textContent=money(group.each);$('#guest-total').textContent=money(group.total)+' за компанию';});

  const memberships=[
    {name:'Массаж спины и плеч',duration:'30 минут',prices:{5:13500,7:17000,10:23000}},
    {name:'Массаж спины и плеч',duration:'45 минут',prices:{5:17500,7:20500,10:27500}},
    {name:'Тайский ойл-массаж',duration:'60 минут',prices:{5:16500,7:22000,10:29000}},
    {name:'Антицеллюлитный массаж',duration:'60 минут',prices:{5:18000,7:23500,10:32000}}
  ];
  let sessions=5;
  const sessionTabs=$$('[data-sessions]');
  function selectSessions(button) { sessions=Number(button.dataset.sessions);markTabs(sessionTabs,button);$('#membership-prices').setAttribute('aria-labelledby',button.id);$$('[data-membership]').forEach((row,i)=>row.querySelector('strong').textContent=money(memberships[i].prices[sessions])); }
  sessionTabs.forEach(button=>button.addEventListener('click',()=>selectSessions(button)));
  keyboardTabs(sessionTabs,selectSessions);

  let giftAmount=5000;
  function updateGift() {
    const selected=$('input[name="gift"]:checked').value;
    const custom=selected==='custom';$('#custom-gift-field').hidden=!custom;
    const amount=custom?$('#custom-gift').valueAsNumber:Number(selected);
    giftAmount=Number.isInteger(amount)&&amount>0&&amount<=1000000?amount:null;
    $('#gift-card-amount').textContent=giftAmount?money(giftAmount):'— ₽';
    $('#custom-gift').setCustomValidity('');
  }
  $$('input[name="gift"]').forEach(input=>input.addEventListener('change',()=>{updateGift();if(input.value==='custom')$('#custom-gift').focus();}));
  $('#custom-gift')?.addEventListener('input',updateGift);

  let restoreFocus=null, requestText='';
  function showDialog(dialog,trigger) { restoreFocus=trigger||document.activeElement; dialog.showModal(); document.body.classList.add('modal-open'); dialog.scrollTop=0; }
  $$('dialog').forEach(dialog=>{
    dialog.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
    dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
    dialog.addEventListener('close',()=>{if(!$('dialog[open]')){document.body.classList.remove('modal-open');if(restoreFocus?.isConnected)restoreFocus.focus({preventScroll:true});}});
  });
  function showBooking(selection,trigger) {
    closeMenu();
    $('#booking-selection').textContent=selection;
    requestText=`Здравствуйте! Хочу обратиться в СПА-салон «Паттайя».\nМоё пожелание: ${selection}.\nПодскажите, пожалуйста, доступное время и условия.`;
    $('#copy-status').textContent='';
    showDialog($('#booking-dialog'),trigger);
  }
  document.addEventListener('click',e=>{
    const bookButton=e.target.closest('[data-book]');if(bookButton)showBooking(bookButton.dataset.book,bookButton);
    const membershipButton=e.target.closest('[data-membership]');
    if(membershipButton){const m=memberships[Number(membershipButton.dataset.membership)];showBooking(`Абонемент: ${m.name}, ${m.duration}, ${sessions} сеансов — ${money(m.prices[sessions])}`,membershipButton);}
  });
  $('#friends-book')?.addEventListener('click',e=>{const g=groupSelection();showBooking(`СПА-девичник: ${g.guests} гостей, ${money(g.each)} за гостя, ${money(g.total)} за компанию`,e.currentTarget);});
  $('#gift-book')?.addEventListener('click',e=>{
    updateGift();
    if(!giftAmount){$('#custom-gift').setCustomValidity('Укажите целый номинал от 1 до 1 000 000 ₽.');$('#custom-gift').reportValidity();return;}
    showBooking(`Подарочный сертификат на ${money(giftAmount)}. Хочу уточнить покупку в салоне`,e.currentTarget);
  });
  $('#copy-request').addEventListener('click',async()=>{
    try{await navigator.clipboard.writeText(requestText);$('#copy-status').textContent='Пожелание скопировано. Вставьте его в ваш диалог с салоном.';}
    catch{const p=$('#booking-selection');const range=document.createRange();range.selectNodeContents(p);const selection=getSelection();selection.removeAllRanges();selection.addRange(range);$('#copy-status').textContent='Выделили пожелание. Скопируйте его вручную и передайте администратору.';}
  });
})();
