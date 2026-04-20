export function renderDetail(detailEl, node) {
  if (!node) {
    detailEl.className = 'card muted';
    detailEl.textContent = '点击图中的节点查看详情。';
    return;
  }

  detailEl.className = 'card';
  detailEl.replaceChildren();

  const titleEl = document.createElement('strong');
  titleEl.textContent = node.id;
  detailEl.append(titleEl);
  detailEl.append(document.createElement('br'));
  detailEl.append(`类型：${node.type}`);
  detailEl.append(document.createElement('br'));
  detailEl.append(`描述：${node.description || '暂无'}`);
}
