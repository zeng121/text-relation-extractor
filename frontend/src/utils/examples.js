export const EXAMPLES = {
  default:
    '张三在字节跳动做后端，李四是张三的同事。两人上周一起负责电商项目，后来王五加入，负责前端。',
  startup:
    '陈晨在星火科技担任产品经理。上个月她和赵磊一起推进增长系统，随后孙宁加入，负责数据分析和运营计划。',
  campus:
    '李华在清华大学人工智能协会负责活动策划。上周王敏加入迎新项目，后来赵宁也参与，负责海报设计。',
};

export const DEFAULT_GRAPH_DATA = {
  nodes: [
    { id: '张三', label: '张三', type: 'person', description: '后端工程师' },
    {
      id: '字节跳动',
      label: '字节跳动',
      type: 'organization',
      description: '组织',
    },
    { id: '电商项目', label: '电商项目', type: 'project', description: '项目' },
  ],
  edges: [
    { source: '张三', target: '字节跳动', label: '就职于' },
    { source: '张三', target: '电商项目', label: '参与' },
  ],
  timeline: [
    {
      id: 't1',
      label: '张三参与电商项目',
      time: '上周',
      detail: '张三上周开始参与电商项目。',
      related_nodes: ['张三', '电商项目'],
    },
  ],
};
