import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm';

const SUPABASE_URL = 'https://ynxmlhgriqalqtecgzdg.supabase.co';
const SUPABASE_KEY = 'sb_publishable_RkecO4SPyQk11YI3CLVyeg_GND51yHm';
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const state = {
  session: null,
  authMode: 'login',
  collections: [],
  items: [],
  activeCollection: 'all',
  viewMode: 'all',
  search: ''
};

const $ = (id) => document.getElementById(id);
const escapeHtml = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
})[char]);

function safeUrl(value) {
  if (!value) return '';
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
  } catch {
    return '';
  }
}

function notify(message) {
  $('toast').textContent = message;
  $('toast').classList.add('show');
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => $('toast').classList.remove('show'), 3200);
}

function setBusy(button, busy, busyLabel, idleLabel) {
  button.disabled = busy;
  button.classList.toggle('busy', busy);
  button.textContent = busy ? busyLabel : idleLabel;
}

function setAuthMode(mode) {
  state.authMode = mode;
  const signup = mode === 'signup';
  $('authSubmit').textContent = signup ? '创建账号' : '登录';
  $('authHint').textContent = signup ? '已有账号？' : '还没有账号？';
  $('authToggle').textContent = signup ? '返回登录' : '创建账号';
  $('authHeadline').innerHTML = signup ? '建立你的<br>私人档案。' : '保存你的<br>视觉宇宙。';
  $('authIntro').textContent = signup
    ? '注册完成后，你会拥有灵感收件箱、视觉参考和待实现三个默认收藏夹。'
    : '把网页、图片、设计稿和一闪而过的念头，归入同一片私人画布。';
  $('password').autocomplete = signup ? 'new-password' : 'current-password';
}

async function submitAuth(event) {
  event.preventDefault();
  const email = $('email').value.trim();
  const password = $('password').value;
  const button = $('authSubmit');
  setBusy(button, true, state.authMode === 'signup' ? '创建中…' : '登录中…', state.authMode === 'signup' ? '创建账号' : '登录');

  try {
    if (state.authMode === 'signup') {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: window.location.href.split('#')[0].split('?')[0] }
      });
      if (error) throw error;
      if (data.session) notify('账号创建完成。');
      else notify('账号已创建，请前往邮箱完成确认，再回来登录。');
    } else {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw error;
    }
  } catch (error) {
    notify(error.message || '操作失败，请稍后重试。');
  } finally {
    setBusy(button, false, '', state.authMode === 'signup' ? '创建账号' : '登录');
  }
}

async function showSession(session) {
  state.session = session;
  const loggedIn = Boolean(session);
  $('authView').classList.toggle('hidden', loggedIn);
  $('appView').classList.toggle('hidden', !loggedIn);
  if (!loggedIn) return;
  $('accountChip').textContent = session.user.email || '已登录';
  await loadData();
}

async function loadData() {
  try {
    const [collectionsResult, itemsResult] = await Promise.all([
      supabase.from('collections').select('*').order('sort_order').order('created_at'),
      supabase.from('inspirations').select('*').order('saved_at', { ascending: false })
    ]);
    if (collectionsResult.error) throw collectionsResult.error;
    if (itemsResult.error) throw itemsResult.error;
    state.collections = collectionsResult.data || [];
    state.items = itemsResult.data || [];
    renderCollections();
    await renderItems();
  } catch (error) {
    notify(error.message || '读取数据失败。');
  }
}

function collectionName(id) {
  return state.collections.find((entry) => entry.id === id)?.name || '未分类';
}

function renderCollections() {
  const total = state.items.length;
  let markup = `<button class="nav-item ${state.activeCollection === 'all' ? 'active' : ''}" data-collection="all"><span>全部灵感</span><span class="nav-count">${total}</span></button>`;

  for (const collection of state.collections) {
    const count = state.items.filter((item) => item.collection_id === collection.id).length;
    markup += `<button class="nav-item ${state.activeCollection === collection.id ? 'active' : ''}" data-collection="${collection.id}"><span>${escapeHtml(collection.name)}</span><span class="nav-count">${count}</span></button>`;
  }

  $('collectionNav').innerHTML = markup;
  $('itemCollection').innerHTML = '<option value="">未分类</option>' + state.collections
    .map((collection) => `<option value="${collection.id}">${escapeHtml(collection.name)}</option>`)
    .join('');

  document.querySelectorAll('[data-collection]').forEach((button) => {
    button.addEventListener('click', async () => {
      state.activeCollection = button.dataset.collection;
      renderCollections();
      await renderItems();
    });
  });
}

async function getImageUrl(item) {
  if (!item.image_url) return '';
  if (!item.image_url.startsWith('storage:')) return safeUrl(item.image_url);
  const path = item.image_url.slice(8);
  const { data, error } = await supabase.storage.from('inspiration-images').createSignedUrl(path, 3600);
  return error ? '' : data.signedUrl;
}

async function renderItems() {
  let filtered = [...state.items];
  if (state.activeCollection !== 'all') {
    filtered = filtered.filter((item) => item.collection_id === state.activeCollection);
  }
  if (state.viewMode === 'favorite') {
    filtered = filtered.filter((item) => item.is_favorite);
  }
  if (state.search) {
    const keyword = state.search.toLowerCase();
    filtered = filtered.filter((item) => [item.title, item.description, item.source_url, item.source_type]
      .filter(Boolean).join(' ').toLowerCase().includes(keyword));
  }

  $('sectionTitle').textContent = state.activeCollection === 'all' ? '全部灵感' : collectionName(state.activeCollection);
  $('sectionMeta').textContent = `${filtered.length} 条内容 · 私人可见`;
  $('emptyState').classList.toggle('hidden', filtered.length > 0);
  if (!filtered.length) {
    $('cardGrid').innerHTML = '';
    return;
  }

  const cards = await Promise.all(filtered.map(async (item) => {
    const imageUrl = await getImageUrl(item);
    const sourceUrl = safeUrl(item.source_url);
    const color = /^#[0-9a-f]{6}$/i.test(item.color_hex || '') ? item.color_hex : '#7546ff';
    const mediaStyle = imageUrl
      ? `background-image:linear-gradient(180deg,transparent 35%,rgba(7,8,12,.2)),url('${imageUrl.replace(/'/g, '%27')}')`
      : `background-image:linear-gradient(135deg,${color},#ff4ea3 56%,#ff8a3d)`;
    const sourceLink = sourceUrl
      ? `<a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">查看来源 ↗</a>`
      : '';

    return `<article class="card">
      <div class="card-media" style="${mediaStyle}">
        <div class="orbit"></div>
        <div class="card-actions">
          <button class="round-btn ${item.is_favorite ? 'on' : ''}" data-favorite="${item.id}" title="收藏">★</button>
          <button class="round-btn" data-remove="${item.id}" title="删除">×</button>
        </div>
      </div>
      <div class="card-body">
        <div class="card-meta"><span>${escapeHtml(item.source_type)}</span><span>${escapeHtml(collectionName(item.collection_id))}</span></div>
        <h4>${escapeHtml(item.title)}</h4>
        <p class="card-desc">${escapeHtml(item.description || '一条等待继续展开的灵感。')}</p>
        ${sourceLink}
      </div>
    </article>`;
  }));

  $('cardGrid').innerHTML = cards.join('');
  document.querySelectorAll('[data-favorite]').forEach((button) => {
    button.addEventListener('click', () => toggleFavorite(button.dataset.favorite));
  });
  document.querySelectorAll('[data-remove]').forEach((button) => {
    button.addEventListener('click', () => removeItem(button.dataset.remove));
  });
}

function openModal() {
  $('modal').classList.remove('hidden');
  setTimeout(() => $('itemTitle').focus(), 30);
}

function closeModal() {
  $('modal').classList.add('hidden');
  $('itemForm').reset();
  $('itemColor').value = '#7546ff';
}

async function uploadImage(file) {
  if (!file) return '';
  if (file.size > 10 * 1024 * 1024) throw new Error('图片不能超过 10 MB。');
  const extension = (file.name.split('.').pop() || 'jpg').toLowerCase();
  const path = `${state.session.user.id}/${crypto.randomUUID()}.${extension}`;
  const { error } = await supabase.storage.from('inspiration-images').upload(path, file, {
    cacheControl: '3600',
    contentType: file.type,
    upsert: false
  });
  if (error) throw error;
  return `storage:${path}`;
}

async function saveItem(event) {
  event.preventDefault();
  const button = $('saveItemBtn');
  setBusy(button, true, '保存中…', '保存灵感');

  try {
    const uploaded = await uploadImage($('itemImageFile').files[0]);
    const payload = {
      user_id: state.session.user.id,
      collection_id: $('itemCollection').value || null,
      title: $('itemTitle').value.trim(),
      description: $('itemDescription').value.trim() || null,
      source_url: $('itemSource').value.trim() || null,
      image_url: uploaded || $('itemImageUrl').value.trim() || null,
      source_type: $('itemType').value,
      is_favorite: $('itemFavorite').checked,
      color_hex: $('itemColor').value
    };

    const { data, error } = await supabase.from('inspirations').insert(payload).select().single();
    if (error) throw error;
    state.items.unshift(data);
    closeModal();
    renderCollections();
    await renderItems();
    notify('灵感已保存。');
  } catch (error) {
    notify(error.message || '保存失败。');
  } finally {
    setBusy(button, false, '', '保存灵感');
  }
}

async function toggleFavorite(id) {
  const item = state.items.find((entry) => entry.id === id);
  if (!item) return;
  const nextValue = !item.is_favorite;
  const { error } = await supabase.from('inspirations').update({ is_favorite: nextValue }).eq('id', id);
  if (error) return notify(error.message);
  item.is_favorite = nextValue;
  await renderItems();
}

async function removeItem(id) {
  if (!window.confirm('确定删除这条灵感吗？')) return;
  const item = state.items.find((entry) => entry.id === id);
  const { error } = await supabase.from('inspirations').delete().eq('id', id);
  if (error) return notify(error.message);

  if (item?.image_url?.startsWith('storage:')) {
    await supabase.storage.from('inspiration-images').remove([item.image_url.slice(8)]);
  }

  state.items = state.items.filter((entry) => entry.id !== id);
  renderCollections();
  await renderItems();
  notify('已删除。');
}

async function createCollection() {
  const name = window.prompt('收藏夹名称');
  if (!name?.trim()) return;
  const { data, error } = await supabase.from('collections').insert({
    user_id: state.session.user.id,
    name: name.trim(),
    sort_order: state.collections.length * 10 + 30
  }).select().single();
  if (error) return notify(error.message);
  state.collections.push(data);
  renderCollections();
  notify('收藏夹已创建。');
}

$('authForm').addEventListener('submit', submitAuth);
$('authToggle').addEventListener('click', () => setAuthMode(state.authMode === 'login' ? 'signup' : 'login'));
$('logoutBtn').addEventListener('click', () => supabase.auth.signOut());
['newItemBtn', 'mobileNewBtn', 'emptyNewBtn'].forEach((id) => $(id).addEventListener('click', openModal));
$('closeModalBtn').addEventListener('click', closeModal);
$('cancelModalBtn').addEventListener('click', closeModal);
$('modal').addEventListener('click', (event) => { if (event.target === $('modal')) closeModal(); });
$('itemForm').addEventListener('submit', saveItem);
$('newCollectionBtn').addEventListener('click', createCollection);
$('searchInput').addEventListener('input', async (event) => {
  state.search = event.target.value.trim();
  await renderItems();
});
document.querySelectorAll('[data-mode]').forEach((button) => {
  button.addEventListener('click', async () => {
    document.querySelectorAll('[data-mode]').forEach((entry) => entry.classList.remove('active'));
    button.classList.add('active');
    state.viewMode = button.dataset.mode;
    await renderItems();
  });
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && !$('modal').classList.contains('hidden')) closeModal();
});

supabase.auth.onAuthStateChange((_event, session) => showSession(session));
const { data: initial } = await supabase.auth.getSession();
await showSession(initial.session);
